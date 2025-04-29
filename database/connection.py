# database/connection.py
# Підключення до бази даних PostgreSQL

import asyncpg
import os
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env
load_dotenv()

# URL для підключення до бази даних
DB_URL = os.getenv("DB_URL")

class Database:
    """
    Клас для роботи з підключенням до бази даних PostgreSQL.
    """
    def __init__(self):
        self.pool = None

    async def connect(self):
        """
        Встановлює з'єднання з базою даних.
        """
        try:
            self.pool = await asyncpg.create_pool(DB_URL)
            print("✅ Підключено до бази даних!")
        except Exception as e:
            print(f"❌ Помилка підключення до бази даних: {e}")

    async def disconnect(self):
        """
        Закриває пул підключень до бази даних.
        """
        if self.pool:
            await self.pool.close()
            print("✅ Підключення до бази даних закрито.")

    async def execute(self, query, *args):
        """
        Виконує SQL-запит без повернення результату.
        """
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query, *args):
        """
        Виконує SQL-запит та повертає всі результати.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query, *args):
        """
        Виконує SQL-запит та повертає один рядок результату.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetchval(self, query, *args):
        """
        Виконує SQL-запит та повертає одне значення.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)