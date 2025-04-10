import os
from dotenv import load_dotenv

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Читання значень
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Перевірка обов'язкових змінних
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не заданий у файлі .env")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не заданий у файлі .env")