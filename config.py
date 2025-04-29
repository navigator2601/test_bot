# config.py
# Файл конфігурації
import os
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу
load_dotenv()

# Токен Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# URL бази даних
DATABASE_URL = os.getenv("DB_URL")

# API-ключ для погоди
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Дані для Telethon
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELETHON_SESSION_NAME = 'kondiki_reader'

# Перевірка наявності обов'язкових змінних
if not BOT_TOKEN:
    raise ValueError("Необхідно вказати BOT_TOKEN у файлі .env")
if not DATABASE_URL:
    raise ValueError("Необхідно вказати DB_URL у файлі .env")
if not WEATHER_API_KEY:
    raise ValueError("Необхідно вказати WEATHER_API_KEY у файлі .env")
if not API_ID:
    raise ValueError("Необхідно вказати API_ID у файлі .env")
if not API_HASH:
    raise ValueError("Необхідно вказати API_HASH у файлі .env")
if not TELEGRAM_PHONE:
    raise ValueError("Необхідно вказати TELEGRAM_PHONE у файлі .env")