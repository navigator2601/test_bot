import asyncpg
from datetime import datetime
from config import DB_URL

# Пул з'єднань з базою даних
pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(dsn=DB_URL)
    async with pool.acquire() as conn:
        # Створюємо таблицю, якщо її немає
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP
            )
        ''')

async def log_user_visit(user_id, username, first_name, last_name):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (id, username, first_name, last_name, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                created_at = EXCLUDED.created_at
        ''', user_id, username, first_name, last_name, datetime.utcnow())