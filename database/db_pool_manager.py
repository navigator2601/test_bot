# database/db_pool_manager.py

import asyncpg
import logging
from config import config # Імпортуємо єдиний об'єкт конфігурації

logger = logging.getLogger(__name__)

_db_pool = None

async def create_db_pool():
    """Створює пул з'єднань з базою даних PostgreSQL."""
    global _db_pool
    if _db_pool is None:
        try:
            # Використовуємо config.database_url для підключення
            _db_pool = await asyncpg.create_pool(config.database_url)
            logger.info("Пул з'єднань до бази даних створено успішно.")
        except Exception as e:
            logger.critical(f"Не вдалося створити пул з'єднань до БД: {e}", exc_info=True)
            raise # Передаємо виняток вище, якщо не вдалося підключитися

async def get_db_pool():
    """Повертає існуючий пул з'єднань."""
    if _db_pool is None:
        logger.warning("Запит на пул з'єднань до БД, але він не був створений. Спроба створити.")
        await create_db_pool() # Автоматично створюємо, якщо його немає
    return _db_pool

async def close_db_pool():
    """Закриває пул з'єднань з базою даних."""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Пул з'єднань до бази даних закрито.")

### **Оновлена функція `init_db_tables`:**

async def init_db_tables():
    """Ініціалізує базу даних, створюючи необхідні таблиці."""
    pool = await get_db_pool() # Отримуємо пул
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Таблиця users
            # Змінено VARCHAR(255) на TEXT для гнучкості
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    access_level INT DEFAULT 0,
                    is_authorized BOOLEAN DEFAULT FALSE,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Таблиця 'users' перевірена/створена.")

            # --- Таблиця telethon_sessions: Змінено структуру для відповідності TelethonClientManager ---
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS telethon_sessions (
                    phone_number VARCHAR(255) PRIMARY KEY, -- Унікальний телефонний номер для сесії
                    session_string TEXT NOT NULL,         -- Сесія Telethon (рядок)
                    api_id INTEGER NOT NULL,              -- API ID, використаний для сесії
                    api_hash VARCHAR(255) NOT NULL,       -- API Hash, використаний для сесії
                    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- ЗМІНА ТУТ
                );
            """)
            logger.info("Таблиця 'telethon_sessions' перевірена/створена.")