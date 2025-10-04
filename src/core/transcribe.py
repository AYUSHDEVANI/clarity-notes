import base64
from openai import OpenAI
from src.utils.config import Config
from src.utils.logger import logger
import httpx
from groq import Groq
import os


def transcribe_audio(file_path: str, language: str = "en") -> dict:
    try:
        # Validate file size (Groq free tier limit: 25MB)
        if(os.path.getsize(file_path) > 25 * 1024 * 1024):
            raise ValueError("Audio file exceed 25MB limit. Use a shorter clip or upgrade tier.")
        
        # Read and encode file to base64 (API requirement)
        with open(file_path, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode("utf-8")


        # Initialize OpenAI client with Groq base URL
        # client = OpenAI(
        #     api_key=Config.GROQ_API_KEY,
        #     base_url="hhtps://api.groq.com/openai/v1",
        #     http_client=httpx.Client(
        # verify=False,  # From step 2
        # timeout=30.0,  # 30s timeout per request
        # limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)  # Connection pooling
        # )
        # )

        client = Groq()


        # Transcribe
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model = Config.WHISPER_MODEL,
                file=audio_file,
                response_format="json",
                language=language,
                temperature=0.0
            )

        logger.info(f"Transcription completed for {file_path} using Groq Whisper")
        segments = response.segments if hasattr(response, 'segments') else []
        # Format transcript with speakers (basic: use timestamps for pseudo-diarization; advanced: integrate whisperx if needed)
        transcript = "\n".join([f"Speaker {i+1} ({seg["start"]}s): {seg["text"]}" for i, seg in enumerate(segments)])
        if not transcript:
            transcript = response.text  # Fallback to plain transcript

        return {"text": response.text, "diarized": transcript}
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise