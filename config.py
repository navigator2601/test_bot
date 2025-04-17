import os
from dotenv import load_dotenv

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API Key для OpenWeather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Перевірка, чи всі необхідні змінні задані
if not BOT_TOKEN:
    raise ValueError("Змінна середовища BOT_TOKEN не задана в .env файлі!")

if not WEATHER_API_KEY:
    raise ValueError("Змінна середовища WEATHER_API_KEY не задана в .env файлі!")