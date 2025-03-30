import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    DB_URI = os.getenv("DATABASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")