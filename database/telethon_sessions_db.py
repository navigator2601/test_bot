# database/telethon_sessions_db.py
import asyncpg
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def save_telethon_session(db_pool: asyncpg.Pool, session_name: str, session_data: bytes):
    """
    Зберігає або оновлює дані сесії Telethon у базу даних.
    session_data має бути bytes (серіалізована сесія).
    """
    async with db_pool.acquire() as conn:
        try:
            await conn.execute(
                """
                INSERT INTO telethon_sessions (session_name, session_data, created_at, updated_at)
                VALUES ($1, $2, $3, $3)
                ON CONFLICT (session_name) DO UPDATE SET
                    session_data = EXCLUDED.session_data,
                    updated_at = EXCLUDED.updated_at
                """,
                session_name,
                session_data,
                datetime.now(timezone.utc)
            )
            logger.info(f"Сесію Telethon '{session_name}' збережено/оновлено в БД.")
        except Exception as e:
            logger.error(f"Помилка при збереженні сесії Telethon '{session_name}': {e}", exc_info=True)
            raise

async def get_telethon_session(db_pool: asyncpg.Pool, session_name: str):
    """
    Отримує дані сесії Telethon з бази даних за іменем.
    Повертає bytes або None.
    """
    async with db_pool.acquire() as conn:
        try:
            record = await conn.fetchrow(
                "SELECT session_data FROM telethon_sessions WHERE session_name = $1",
                session_name
            )
            if record:
                logger.info(f"Сесію Telethon '{session_name}' завантажено з БД.")
                return record['session_data']
            else:
                logger.info(f"Сесію Telethon '{session_name}' не знайдено в БД.")
                return None
        except Exception as e:
            logger.error(f"Помилка при отриманні сесії Telethon '{session_name}': {e}", exc_info=True)
            raise

async def delete_telethon_session(db_pool: asyncpg.Pool, session_name: str):
    """
    Видаляє сесію Telethon з бази даних.
    """
    async with db_pool.acquire() as conn:
        try:
            await conn.execute(
                "DELETE FROM telethon_sessions WHERE session_name = $1",
                session_name
            )
            logger.info(f"Сесію Telethon '{session_name}' видалено з БД.")
        except Exception as e:
            logger.error(f"Помилка при видаленні сесії Telethon '{session_name}': {e}", exc_info=True)
            raise