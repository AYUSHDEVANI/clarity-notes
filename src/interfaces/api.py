from datetime import datetime
import json
import sqlite3
import time
from typing import Optional
import uuid
import wave
from fastapi import FastAPI, Form, Query, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import socketio
import sys
import os

from src.utils.config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pyaudio
import uvicorn
from src.utils.logger import logger
from src.graphs.meeting_workflow import run_workflow
from src.interfaces.models import FeedbackInput, MeetingInput


app = FastAPI()

# Socket.io Integration
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="http://localhost:3000")
app.mount("/socket.io", socketio.ASGIApp(sio))

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model = Config.MODEL_NAME,
    temperature=0.3,
    groq_api_key = Config.GROQ_API_KEY
)

# DB for analytics
conn = sqlite3.connect("instance/analytics.db", check_same_thread=False)\

conn.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
             meeting_id TEXT PRIMARY KEY,
             timestamp DATETIME,
             file_path TEXT,
             language TEXT,
             transcript TEXT,
             summary TEXT,
             actions TEXT,
             diarized_transcript TEXT,
             industry TEXT,
             user_id TEXT,
             meeting_title TEXT
             )
        """)

conn.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY,
        meeting_id TEXT,
        rating INT,
        comments TEXT,
        FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
    )
""")

conn.commit()

# Global flag for recording control
recording_active = False

# Store latest meeting id for chat context
latest_meeting_id = None

# Store recent transcription results for Q&A context
recent_results = {}


@app.post("/process_meeting")
async def process_meeting(input: str = Form(...), file: UploadFile = File(None)):
    try:
        # Parse input JSON
        input_data = json.loads(input)
        logger.debug(f"Input data: {input_data}")
        meeting_input = MeetingInput.from_dict(input_data)
        
        # Validate channel if notify_slack is true
        if meeting_input.notify_slack and not meeting_input.channel:
            raise ValueError("Channel required when notify_slack is true")

        # Prioritize uploaded file; ignore file_path in input
        if file:
            if file.size > 25 * 1024 * 1024:
                raise ValueError("File size exceeds 25MB limit")
            file_path = f"uploads/{file.filename}"
            os.makedirs("uploads", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(await file.read())
        elif meeting_input.file_path and os.path.exists(meeting_input.file_path):
            file_path = meeting_input.file_path
        else:
            raise ValueError("A file must be uploaded or a valid file_path provided")

        result = run_workflow(
            file_path = file_path,
            output_path = f"notes_{os.path.basename(file_path)}.md",
            language = meeting_input.language,
            notify_slack = meeting_input.notify_slack,
            channel = meeting_input.channel,
            industry = meeting_input.industry,
            custom_prompt_description = meeting_input.custom_prompt_description
        )

        logger.debug(f"Process meeting result: {result}")

        # Store in DB
        meeting_id = str(uuid.uuid4())
        timestamp_now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO meetings (meeting_id, timestamp, file_path, language, transcript, \
                summary, actions, diarized_transcript, industry, user_id, meeting_title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    meeting_id,
                    timestamp_now, 
                    file_path,
                    meeting_input.language,
                    result.get("transcript", {}).get("diarized", ""),
                    result.get("summary", {}).get("summary", ""),
                    result.get("actions", ""),
                    result.get("transcript", {}).get("diarized", ""),
                    meeting_input.industry,
                    meeting_input.user_id,
                    meeting_input.meeting_title

                )
        )

        # Emit new meeting to all connected clients
        await sio.emit("new_meeting", {
            "meeting_id": meeting_id,
            "meeting_title": meeting_input.meeting_title,
            "timestamp": timestamp_now
        })
        
        conn.commit()
        global latest_meeting_id
        latest_meeting_id = meeting_id  # Update latest meeting id for chat context
        return {"meeting_id": meeting_id, "result": result}
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid input JSON")
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch processing endpoint
@app.post("/process_batch")
async def process_batch(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok = True)

        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        result = run_workflow(file_path, f"notes_{file.filename}.md")
        results.append(result)
        recent_results[file_path] = result # store for Q&A

        # Store in DB
        meeting_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO meetings (meeting_id, timestamp, file_path, language, transcript, summary, actions, diarized_transcript, industry, user_id, meeting_title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                meeting_id,
                datetime.now().isoformat(),
                file_path,
                "en",  # Default language; adjust if needed
                result.get("transcript", {}).get("diarized", ""),
                result.get("summary", {}).get("summary", ""),
                result.get("actions", ""),
                result.get("transcript", {}).get("diarized", ""),
                "General",  # Default industry
                "anonymous",  # Default user
                f"Batch Meeting {file.filename}"  # Default title
            )
        )
        conn.commit()
        global latest_meeting_id
        latest_meeting_id = meeting_id


    return {"results": results}

# Real time endpoint (stream audio)
@app.post("/real_time_transcribe")
async def real_time_transcribe(
    background_tasks: BackgroundTasks, 
    language: str = "en",
    industry: str = "General",
    user_id: str = "anonymous",
    meeting_title: str = "real-Time meeting",
    custom_prompt_description: Optional[str] = None
):
    global recording_active
    if recording_active:
        raise HTTPException(status_code=400, detail="Recording already in progress")


    def record_and_process():
        global recording_active
        recording_active = True
        try: 
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            RECORD_SECONDS = 30

            p = pyaudio.PyAudio()

            stream = p.open(
                format=FORMAT, 
                channels=CHANNELS, 
                rate=RATE, 
                input=True, 
                frames_per_buffer=CHUNK
            )
            frames = []

            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            if frames:
                # Use consistent path relative to project root
                upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, "real_time.wav")
                logger.info(f"Saving audio to {file_path}")
                try:
                    wf = wave.open(file_path, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                except Exception as e:
                    logger.error(f"Failed to save audio file: {str(e)}")
                    raise
                if os.path.exists(file_path):
                    logger.info(f"Audio saved successfully to {file_path}, size: {os.path.getsize(file_path)} bytes")
                else:
                    logger.error(f"Failed to create audio file: {file_path}")
                    raise ValueError("Failed to save audio file")
                output_path = os.path.join(upload_dir, "real_time_notes.md")
                result = run_workflow(
                    file_path, 
                    output_path, 
                    language=language,
                    custom_prompt_description =  custom_prompt_description
                )
                logger.debug(f"Real-time transcription result: {result}")
                # Store in DB
                meeting_id = str(uuid.uuid4())
                timestamp_now = datetime.now().isoformat()
                conn.execute(
                    "INSERT INTO meetings (meeting_id, timestamp, file_path, language, transcript, summary, actions, diarized_transcript, industry, user_id, meeting_title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        meeting_id,
                        timestamp_now,
                        "real_time.wav",
                        language,
                        result.get("transcript", {}).get("diarized", ""),
                        result.get("summary", {}).get("summary", ""),
                        result.get("actions", ""),
                        result.get("transcript", {}).get("diarized", ""),
                        industry,
                        user_id,
                        meeting_title
                    )
                )

                
                conn.commit()
                global latest_meeting_id
                latest_meeting_id = meeting_id

        except Exception as e:
            logger.error(f"Recording error: {e}")
            raise

        finally:
            recording_active = False

    background_tasks.add_task(record_and_process)
    return {"status": "Recording started", "meeting_id": latest_meeting_id}

@app.post("/stop_recording")
async def stop_recording():
    global recording_active
    if not recording_active:
        raise HTTPException(status_code=400, detail="No active recording")
    recording_active = False
    return {"status": "Recording stopped"}

@app.get("/get_transcription_results")
async def get_transcription_results():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "uploads", "real_time.wav")
    output_file = os.path.join(base_dir, "uploads", "real_time_notes.md")
    logger.info(f"Checking for audio file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        raise HTTPException(status_code=404, detail="No recorded audio found")
    logger.info(f"Waiting for transcription output: {output_file}")
    for _ in range(15):  # 10-second timeout
        if os.path.exists(output_file):
            try:
                result = run_workflow(file_path, output_file, language="en")
                logger.debug(f"Transcription results: {result}")
                return result
            except Exception as e:
                logger.error(f"Error retrieving transcription results: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to retrieve transcription results: {str(e)}")
        time.sleep(1)
    logger.error(f"Transcription output not found: {output_file}")
    raise HTTPException(status_code=404, detail="Transcription results not yet available")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackInput):
    try:
        conn.execute(
            "INSERT INTO feedback (meeting_id, rating, comments) VALUES (?, ?, ?)",
            (feedback.meeting_id, feedback.rating, feedback.comments)
        )
        conn.commit()
        return {"status": "Feedback saved"}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_meetings")
async def get_meetings():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT meeting_id, meeting_title, timestamp FROM meetings ORDER BY timestamp DESC")
        meetings = [{"meeting_id": row[0], "meeting_title": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
        return {"meetings": meetings}
    except Exception as e:
        logger.error(f"Error fetching meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Socket.io events for live chat Q&A
@sio.on("connect")
async def handle_connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit("message", {"type": "status", "content": "Connected to chat"}, room=sid)

@sio.on("disconnect")
async def handle_disconnect(sid):
    logger.info(f"Client Disconnected: {sid}")

@sio.on("message")
async def handle_message(sid, data):
    global latest_meeting_id
    from src.graphs.meeting_workflow import run_workflow
    logger.info(f"Message received from {sid}: {data}")

    try:
        meeting_id = data.get("meeting_id", latest_meeting_id)
        if not meeting_id:
            await sio.emit("message",
                           {
                               "type": "error",
                               "content": " No recent meeting found. process a meeting first" 
                           })
            return 

        # Fetch latest meeting context from DB
        cursor = conn.cursor()
        cursor.execute(
            "SELECT transcript, summary FROM meetings WHERE meeting_id = ?",
            (meeting_id,)
        )

        row = cursor.fetchone()
        if not row:
            await sio.emit("message",
                           {
                               "type": "error",
                               "content": "No meeting context found." 
                           })
            return
        
        transcript, summary = row

        # Run Langgraph workflow with chat message
        result = run_workflow(
            file_path="", # Not need for Q&A
            output_path="",
            language="en",
            chat_message=data.get("message", ""),
            transcript = transcript,
            summary = summary
        
        )

        response = {
            "type": "message",
            "content": result.get("qa_response", "No response generated"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        await sio.emit("message",response, room=sid)

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        await sio.emit("message",
                       {
                           "type": "error",
                           "content": f"Error: {str(e)}",
                           "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                       }, room=sid)


app.get("/analytics")
async def get_analytics(industry: Optional[str] = Query(None)):
    """Return Aggregate insights across meetings"""

    cursor = conn.cursor()

    if industry:
        cursor.execute("SELECT actions, summary FROM meetings WHERE industry=?", (industry,))
    else:
        cursor.execute("SELECT actions, summary FROM meetings")

    action_trends = {}
    sentiment_counts = {
        "Positive": 0,
        "Neutral" : 0,
        "Negative": 0
    }
    total_meetings = 0

    for row in cursor.fetchall():
        actions_json, summary_text = row
        total_meetings += 1

        # Aggregate action trends
        if actions_json:
            try:
                actions_list = json.loads(actions_json)
                for a in actions_list:
                    desc = a.get("description", "Unknown")
                    action_trends[desc] = action_trends.get(desc, 0) + 1
            except Exception as e:
                logger.error(f"Error parsing actions JSON: {e}")

        # Aggregate sentiment from summary (if sentiment included)
        if summary_text:
            if "positive" in summary_text.lower():
                sentiment_counts["Positive"] += 1
            elif "neutral" in summary_text.lower():
                sentiment_counts["Neutral"] += 1
            else:
                sentiment_counts["Negative"] += 1

    return {
        "total_meetings": total_meetings,
        "action_trends": action_trends,
        "sentiment_counts": sentiment_counts
    }


app.post("/ai_insight")
async def ai_insight(query: str = Form(...), industry: Optional[str] = Query(None)):
    """Return conversational insights across multiple meetings"""

    cursor = conn.cursor()

    if industry:
        cursor.execute("SELECT summary FROM meetings WHERE industry=?", (industry,))
    else:
        cursor.execute("SELECT summary FROM meetings")

    summaries = "\n".join([row[0] for row in cursor.fetchall() if row[0]])

    prompt_template = f"""
You are AI analyst. Given the following meeting summaries across multiple meetings:

{summaries}

Answer the user query conciesly:
{query}
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)

    try:
        response = llm.invoke([
            {
                "role": "user",
                "content": prompt
            }
        ])

        return {"answer": response.content}
    
    except Exception as e:
        logger.error(f"AI Insight error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,)
