import asyncpg
import os
from dotenv import load_dotenv

# Завантаження змінних з .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задано. Перевірте файл .env.")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Підключено до бази даних!")
    return conn