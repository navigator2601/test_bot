import os
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу  
load_dotenv()

# Отримання значень змінних середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")

# Перевірка, чи всі необхідні змінні задані
if not BOT_TOKEN:
    raise ValueError("Змінна середовища BOT_TOKEN не задана в .env файлі!")

if not DB_URL:
    raise ValueError("Змінна середовища DB_URL не задана в .env файлі!")
