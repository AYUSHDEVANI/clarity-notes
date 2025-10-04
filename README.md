# ✨ Clarity Notes – AI-Powered Meeting Assistant

**Tagline:** Transform your meetings into actionable insights with AI-driven summaries, action items, and analytics 📊🤖

---

## 🎥 Demo Video

Check out the demo of Clarity Notes in action:

<!-- ![Clarity Notes Demo](assets/Clarity-notes-2.mp4) -->

<video width="600" controls>
  <source src="assets/demo_video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

## 📝 Project Overview

Clarity Notes is an **AI-powered meeting notes application** designed to:

- 🎤 Transcribe audio/video meetings in multiple languages.
- 🧾 Summarize meeting transcripts with key decisions and outcomes.
- ✅ Extract structured action items with assignees, deadlines, and priority.
- 💬 Provide live Q&A interaction based on meeting context.
- 📈 Generate cross-meeting analytics and insights dashboards.
- 🔔 Optionally notify Slack channels with meeting summaries and actions.

This application leverages **LangChain**, **LangGraph**, and **Groq AI** for LLM-driven insights, combined with a **React frontend** for visualization.

---

## 🚀 Current Features

### Core Functionalities

1. **Meeting Transcription** 🎧  
    - Supports file uploads (mp3, wav) and real-time audio recording.  
    - Multi-language support.  
    - Diarized transcripts for speaker identification.

    ![Upload Meeting Audio](assets/upload-tab.png)

2. **Summarization** ✍️  
    - Generates concise summaries highlighting decisions, outcomes, and discussion points.  
    - Industry-specific summaries (Finance, Healthcare, Marketing, Education).

3. **Action Item Extraction** ✅  
    - Identifies tasks, assigns responsibility, sets deadlines, and prioritizes actions.  
    - Industry-specific prompts for compliance and privacy.

4. **Real-Time Q&A Chat** 💬  
    - Floating AI assistant for asking questions based on latest meeting transcript and summary.

    ![Live Q&A Chat](assets/live-Q&A-chat.png)

5. **Feedback Collection** 🌟  
    - Users can submit ratings and comments for each meeting.

6. **Analytics Dashboard** 📊  
    - Meetings over time.  
    - Action trends across meetings.  
    - Sentiment analysis (Positive, Neutral, Negative) for insights.  
    - Industry-specific analytics.

    ![Dashboard](assets/dashboard-tab.png)


7. **Slack Notifications** 🔔  
    - Optional automated Slack notifications with summaries and action items.


8. **Real-Time Recording** 🎤  
    - Capture live meetings and stream for real-time transcription.  

    ![Real-Time](assets/real-time-tab.png)

9. **Meeting Results** 📝  
    - View extracted action items, summaries, and diarized transcripts.  

    ![Result 1](assets/result-tab.png)  
    ![Result 2](assets/result-tab-2.png)

---

## 🌟 Future / Unique Features

- **Cross-Meeting Insights** 🔍  
  Detect trends in action items, recurring decisions, and risks across multiple meetings.

- **Predictive Intelligence** 📈  
  Estimate risk of task delay and ROI tracking for enterprise meetings.

- **Customizable Prompts** 🛠️  
  Generate tailored summary and action prompts for unique business needs.

- **Enhanced Visualizations** 📉  
  Advanced charts and KPI dashboards for executives and team leads.

- **AI-Powered Recommendations** 🤖  
  Suggest next steps or improvements based on historical meeting patterns.

---

## 🗂️ Folder Structure

```bash
backend/
├── src/
│   ├── api.py
│   ├── core/
│   ├── graphs/
│   ├── interfaces/
│   └── utils/
frontend/
├── src/
│   ├── components/
│   ├── App.js
│   └── index.js
uploads/      # Auto-generated files (gitignored)
instance/     # Database (gitignored)
assets/       # Screenshots
```

---

## ⚡ Workflow / Flow of Data

1. **Upload/Record Meeting Audio** 🎤  
2. **Transcription** → Convert speech to text 📝  
3. **Generate Custom Prompts** 🛠️  
4. **Summarization** ✍️ → Key points, decisions, and insights  
5. **Action Extraction** ✅ → Tasks, deadlines, assignees  
6. **Optional Slack Notification** 🔔 → Send summary and actions  
7. **Save Outputs** 💾 → Markdown / Database  
8. **Analytics Dashboard** 📊 → Insights across meetings  
9. **Real-Time Q&A** 💬 → Ask questions from AI assistant  

## **Flow Diagram (Textual Representation):**

```mermaid
flowchart TD
    A[Audio Upload / Real-Time Recording] --> B[Transcription]
    B --> C[Generate Custom Prompts]
    C --> D[Summarization]
    D --> E[Action Extraction]
    E --> F[Save Output]
    E --> G[Slack Notification]
    F --> H[Analytics & Dashboards]
    H <--> I[Real-Time Q&A Chat]
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python, SQLite 🐍  
- **Frontend:** React, Bootstrap, Recharts ⚛️  
- **AI/LLM Integration:** LangChain, LangGraph, ChatGroq 🤖  
- **Audio Processing:** PyAudio, Wave 🎧  
- **Real-Time Communication:** Socket.io 💬

---

## ⚙️ Installation

### Backend

```bash
git clone <repo-url>
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env      # Fill API keys and configs
uvicorn src.interfaces.api:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

---

## 🖥️ Usage

1. Open the frontend in the browser (default: http://localhost:3000).
2. Upload a meeting audio file or use real-time recording.
3. View automatically generated summary, action items, and insights dashboard.
4. Ask questions to the AI chat assistant.
5. Submit feedback for each meeting.
6. Explore analytics for trends across meetings.

---

## 🔔 Enabling Slack Notifications

Clarity Notes can optionally send meeting summaries and action items to your Slack workspace. Follow these steps to set up Slack notifications:

### **Step 1: Create a Slack App**
1. Go to [Slack API: Your Apps](https://api.slack.com/apps).  
2. Click **Create New App → From scratch**.  
3. Name your app (e.g., `ClarityNotesBot`) and choose your Slack workspace.  
4. Click **Create App** ✅

---

### **Step 2: Add Bot to Workspace**
1. Navigate to **OAuth & Permissions** in your app settings.  
2. Scroll to **Scopes → Bot Token Scopes** and add:  
   - `chat:write` → To send messages.  
   - `channels:read` → To read channel list (optional).  
   - `channels:join` → To let the bot join channels automatically.  
3. Click **Install to Workspace** and **Allow**.  
4. You will get a **Bot User OAuth Token** starting with `xoxb-xxxxxxxx`.  
   > This is your `SLACK_BOT_TOKEN`.

---

### **Step 3: Add Bot to a Channel**
1. Open Slack and go to the channel where you want notifications.  
2. Type the command:  

```text
/invite @ClarityNotesBot
```
3. Press Enter. The bot can now send messages to this channel.

### **Step 4: Set Environment Variables (.env)**
In your backend project directory, create or update the .env file:
```bash
# Slack Bot configuration
SLACK_BOT_TOKEN=xoxb-your-token-here

# AI / LLM Configuration
GROQ_API_KEY=your-groq-api-key-here

```



## 🤝 Contributing

- Fork the repository.
- Create a new feature branch.
- Ensure code quality and run tests.
- Submit a pull request with a clear description.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📧 Contact

For questions or support, contact Ayush Devani at ayushdevani0018@gmail.com.

---


