# database/users_db.py
import asyncpg
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List # Додано для більш точної типізації

logger = logging.getLogger(__name__)

async def get_user(db_pool: asyncpg.Pool, user_id: int) -> Optional[Dict]:
    """Отримує користувача з бази даних за ID."""
    async with db_pool.acquire() as conn:
        # fetchrow повертає Record, який можна перетворити на dict
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return dict(user) if user else None

async def add_user(
    db_pool: asyncpg.Pool,
    user_id: int,
    username: Optional[str], # username може бути None
    first_name: Optional[str], # first_name може бути None
    last_name: Optional[str] # last_name може бути None
) -> None:
    """Додає нового користувача до бази даних або оновлює існуючого."""
    async with db_pool.acquire() as conn:
        current_time = datetime.now(timezone.utc)
        await conn.execute(
            """
            INSERT INTO users (id, username, first_name, last_name, is_authorized, access_level, registered_at, last_activity)
            VALUES ($1, $2, $3, $4, TRUE, 0, $5, $5)
            ON CONFLICT (id) DO UPDATE SET
                username = COALESCE(EXCLUDED.username, users.username), -- Оновлюємо, тільки якщо EXCLUDED.username не NULL
                first_name = COALESCE(EXCLUDED.first_name, users.first_name),
                last_name = COALESCE(EXCLUDED.last_name, users.last_name),
                last_activity = EXCLUDED.last_activity
            """,
            user_id,
            username,
            first_name,
            last_name,
            current_time
        )
        logger.info(f"Користувача {user_id} додано/оновлено в БД.")

async def update_user_activity(db_pool: asyncpg.Pool, user_id: int) -> None:
    """Оновлює час останньої активності користувача."""
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET last_activity = $1 WHERE id = $2",
            datetime.now(timezone.utc),
            user_id
        )
        logger.info(f"Оновлено last_activity для користувача {user_id}.")

async def get_user_access_level(db_pool: asyncpg.Pool, user_id: int) -> int:
    """
    Отримує рівень доступу користувача з бази даних.
    Повертає 0, якщо користувач не знайдений або access_level відсутній.
    """
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow("SELECT access_level FROM users WHERE id = $1", user_id)
        # Перевіряємо, чи запис існує і чи містить 'access_level'
        if record and 'access_level' in record:
            return record['access_level']
        return 0

async def get_all_users(db_pool: asyncpg.Pool) -> List[Dict]:
    """
    Отримує список всіх користувачів з бази даних.
    """
    async with db_pool.acquire() as conn:
        try:
            # Вибираємо всі потрібні поля, використовуючи 'registered_at'
            users = await conn.fetch("SELECT id, username, first_name, last_name, access_level, is_authorized, registered_at, last_activity FROM users ORDER BY registered_at DESC")
            # Перетворюємо записи на словники для зручності
            return [dict(u) for u in users]
        except Exception as e:
            logger.error(f"Помилка при отриманні всіх користувачів з БД: {e}", exc_info=True)
            return []

async def update_user_authorization_status(db_pool: asyncpg.Pool, user_id: int, is_authorized: bool) -> None:
    """
    Оновлює статус авторизації користувача в базі даних.
    """
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_authorized = $1 WHERE id = $2",
            is_authorized,
            user_id
        )
        logger.info(f"Статус авторизації користувача {user_id} встановлено на {is_authorized}.")

# --- НОВА ФУНКЦІЯ: Оновлення рівня доступу користувача ---
async def update_user_access_level(db_pool: asyncpg.Pool, user_id: int, new_level: int) -> None:
    """
    Оновлює рівень доступу користувача в базі даних.
    """
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET access_level = $1 WHERE id = $2",
            new_level,
            user_id
        )
        logger.info(f"Рівень доступу користувача {user_id} оновлено до {new_level}.")