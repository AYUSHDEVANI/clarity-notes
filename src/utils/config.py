import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "llama-3.3-70b-versatile"
    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    WHISPER_MODEL = "whisper-large-v3-turbo"

    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")




if not Config.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in .env")