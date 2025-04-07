import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
GEMINI_SERVICE_ACCOUNT = os.getenv('GEMINI_SERVICE_ACCOUNT')

# Перевірка змінних оточення
if not API_TOKEN:
    raise ValueError("No API token provided. Please check your .env file.")
if not DATABASE_URL:
    raise ValueError("No database URL provided. Please check your .env file.")
if not GEMINI_SERVICE_ACCOUNT:
    raise ValueError("No Gemini service account provided. Please check your .env file.")