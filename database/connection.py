import asyncpg
from config import DB_URL

async def connect_to_db():
    try:
        conn = await asyncpg.connect(DB_URL)
        print("Підключення до бази даних успішно!")
        await conn.close()
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")