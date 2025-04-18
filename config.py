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

# Перевірка наявності обов'язкових змінних
if not BOT_TOKEN:
    raise ValueError("Необхідно вказати BOT_TOKEN у файлі .env")
if not DATABASE_URL:
    raise ValueError("Необхідно вказати DB_URL у файлі .env")
if not WEATHER_API_KEY:
    raise ValueError("Необхідно вказати WEATHER_API_KEY у файлі .env")