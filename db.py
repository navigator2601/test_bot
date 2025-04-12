import os
import asyncpg
from dotenv import load_dotenv

# Завантаження змінних оточення з .env
load_dotenv()

# Рядок підключення до бази даних
DB_URL = os.getenv("DB_URL")

async def get_available_brands() -> list:
    """Отримує список брендів, у яких є моделі"""
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT DISTINCT b.name
        FROM brands b
        JOIN models m ON b.id = m.brand_id
        WHERE m.id IS NOT NULL
    """)
    await conn.close()
    return [row['name'] for row in rows]