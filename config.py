from dotenv import load_dotenv
import os

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Дані для підключення до бази даних
DB_URL = os.getenv("DB_URL")