# database/users_db.py
import asyncpg
import os
import logging
from datetime import datetime, timezone # Додано timezone

_pool = None # Змінна для зберігання пулу з'єднань з базою даних

users_db_logger = logging.getLogger(__name__) # Логер для цього модуля

async def create_db_pool():
    """Ініціалізує пул з'єднань з базою даних."""
    global _pool
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        users_db_logger.critical("DATABASE_URL не встановлено в .env файлі!")
        return False
    try:
        _pool = await asyncpg.create_pool(db_url)
        users_db_logger.info("Пул з'єднань з базою даних PostgreSQL створено, використовуючи DATABASE_URL.")
        return True
    except Exception as e:
        users_db_logger.critical(f"Не вдалося підключитися до бази даних PostgreSQL: {e}", exc_info=True)
        return False

async def close_db_pool():
    """Закриває пул з'єднань з бази даних."""
    global _pool
    if _pool:
        await _pool.close()
        users_db_logger.info("Пул з'єднань з базою даних PostgreSQL закрито.")

async def get_user_data(user_id: int) -> dict | None:
    """
    Отримує дані користувача за user_id.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return None
    async with _pool.acquire() as connection:
        user = await connection.fetchrow(
            "SELECT id, username, first_name, last_name, created_at, is_authorized, access_level, last_activity, registered_at "
            "FROM users WHERE id = $1",
            user_id
        )
        return dict(user) if user else None

async def update_user_activity(user_id: int):
    """
    Оновлює час останньої активності користувача.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return
    async with _pool.acquire() as connection:
        await connection.execute(
            "UPDATE users SET last_activity = $1 WHERE id = $2",
            datetime.now(timezone.utc), user_id # Замінено на datetime.now(timezone.utc)
        )

async def add_new_user(user_id: int, username: str | None, first_name: str | None, last_name: str | None):
    """
    Додає нового користувача до бази даних.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return
    async with _pool.acquire() as connection:
        try:
            await connection.execute(
                """
                INSERT INTO users (id, username, first_name, last_name, created_at, last_activity, is_authorized, access_level, registered_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_activity = EXCLUDED.last_activity
                """,
                user_id, username, first_name, last_name, datetime.now(timezone.utc), datetime.now(timezone.utc), True, 0, datetime.now(timezone.utc) # Замінено на datetime.now(timezone.utc)
            )
            users_db_logger.info(f"Користувач {user_id} успішно доданий/оновлений в БД.")
        except Exception as e:
            users_db_logger.error(f"Помилка при додаванні нового користувача {user_id}: {e}", exc_info=True)


async def get_all_users() -> list:
    """
    Повертає список всіх користувачів з бази даних.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return []
    
    async with _pool.acquire() as connection:
        try:
            users = await connection.fetch(
                "SELECT id, username, first_name, last_name, created_at, is_authorized, access_level, last_activity, registered_at "
                "FROM users ORDER BY created_at DESC"
            )
            return [dict(user) for user in users]
        except Exception as e:
            users_db_logger.error(f"Помилка при отриманні всіх користувачів: {e}", exc_info=True)
            return []

async def update_user_status(user_id: int, is_authorized: bool) -> bool:
    """
    Оновлює статус is_authorized для користувача.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return False
    
    async with _pool.acquire() as connection:
        try:
            await connection.execute(
                "UPDATE users SET is_authorized = $1, last_activity = $2 WHERE id = $3",
                is_authorized, datetime.now(timezone.utc), user_id # Замінено на datetime.now(timezone.utc)
            )
            users_db_logger.debug(f"Оновлено статус is_authorized для користувача ID: {user_id} на {is_authorized}.")
            return True
        except Exception as e:
            users_db_logger.error(f"Помилка при оновленні статусу користувача ID: {user_id}: {e}", exc_info=True)
            return False

async def update_user_access_level(user_id: int, access_level: int) -> bool:
    """
    Оновлює рівень доступу користувача.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return False
    
    async with _pool.acquire() as connection:
        try:
            await connection.execute(
                "UPDATE users SET access_level = $1, last_activity = $2 WHERE id = $3",
                access_level, datetime.now(timezone.utc), user_id # Замінено на datetime.now(timezone.utc)
            )
            users_db_logger.debug(f"Оновлено рівень доступу для користувача ID: {user_id} на {access_level}.")
            return True
        except Exception as e:
            users_db_logger.error(f"Помилка при оновленні рівня доступу користувача ID: {user_id}: {e}", exc_info=True)
            return False

### **НОВА ФУНКЦІЯ**: `add_new_user_manually`

async def add_new_user_manually(user_id: int, first_name: str = "Невідомий", last_name: str = None, username: str = None, is_authorized: bool = True, access_level: int = 0) -> bool:
    """
    Додає нового користувача до бази даних вручну.
    Призначений для використання адміністратором, дозволяє встановити
    статус авторизації та рівень доступу за замовчуванням.
    """
    if _pool is None:
        users_db_logger.error("Пул з'єднань з БД не ініціалізовано.")
        return False

    async with _pool.acquire() as connection:
        try:
            # Перевіряємо, чи користувач вже існує
            existing_user = await connection.fetchrow("SELECT id FROM users WHERE id = $1", user_id)
            if existing_user:
                users_db_logger.warning(f"Спроба додати існуючого користувача вручну: {user_id}")
                return False # Користувач вже існує, не додаємо

            await connection.execute(
                """
                INSERT INTO users (id, username, first_name, last_name, created_at, last_activity, is_authorized, access_level, registered_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                user_id, username, first_name, last_name, datetime.now(timezone.utc), datetime.now(timezone.utc), is_authorized, access_level, datetime.now(timezone.utc) # Замінено на datetime.now(timezone.utc)
            )
            users_db_logger.info(f"Користувача {user_id} додано вручну до бази даних.")
            return True
        except Exception as e:
            users_db_logger.error(f"Помилка при ручному додаванні користувача {user_id}: {e}", exc_info=True)
            return False