import os
from dotenv import load_dotenv

load_dotenv()  # Завантажує змінні середовища з .env

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Телеграм токен
DATABASE_URL = os.getenv("DATABASE_URL")  # Підключення до Postgres