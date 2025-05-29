# database/users_db.py
import asyncpg
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def get_user(db_pool: asyncpg.Pool, user_id: int):
    """Отримує користувача з бази даних за ID."""
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user

async def add_user(db_pool: asyncpg.Pool, user_id: int, username: str, first_name: str, last_name: str):
    """Додає нового користувача до бази даних."""
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (id, username, first_name, last_name, is_authorized, access_level, registered_at, last_activity)
            VALUES ($1, $2, $3, $4, TRUE, 0, $5, $5)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                last_activity = EXCLUDED.last_activity
            """,
            user_id,
            username,
            first_name,
            last_name,
            datetime.now(timezone.utc) # Використовуємо UTC для часових міток
        )
        logger.info(f"Користувача {user_id} додано/оновлено в БД.")

async def update_user_activity(db_pool: asyncpg.Pool, user_id: int):
    """Оновлює час останньої активності користувача."""
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET last_activity = $1 WHERE id = $2",
            datetime.now(timezone.utc), # Використовуємо UTC для часових міток
            user_id
        )
        logger.info(f"Оновлено last_activity для користувача {user_id}.")