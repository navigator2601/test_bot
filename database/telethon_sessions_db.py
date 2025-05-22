# database/telethon_sessions_db.py
import asyncpg
import os
import pickle
from utils.logger import logger
from telethon.sessions import StringSession # <--- Імпортуємо StringSession

db_session_logger = logger.getChild("telethon_sessions_db")

# Глобальна змінна для пулу з'єднань Telethon
_session_pool = None

async def init_telethon_sessions_db():
    """
    Ініціалізує пул з'єднань з базою даних PostgreSQL для Telethon сесій.
    Повертає True у разі успіху, False у разі помилки.
    """
    global _session_pool
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        db_session_logger.critical("Змінна оточення 'DATABASE_URL' не встановлена.")
        return False
    
    try:
        _session_pool = await asyncpg.create_pool(DATABASE_URL)
        db_session_logger.info("Пул з'єднань з базою даних PostgreSQL для Telethon сесій створено.")
        # Таблиця вже мала бути створена за допомогою наданого SQL.
        # await _create_telethon_sessions_table() # Цей виклик вже не потрібен, якщо таблиця створюється SQL-скриптом
        return True
    except Exception as e:
        db_session_logger.critical(f"Помилка при ініціалізації пулу з'єднань з БД Telethon сесій: {e}", exc_info=True)
        return False

async def close_telethon_sessions_db():
    """Закриває пул з'єднань з бази даних Telethon сесій."""
    global _session_pool
    if _session_pool:
        await _session_pool.close()
        db_session_logger.info("Пул з'єднань з базою даних PostgreSQL для Telethon сесій закрито.")
        _session_pool = None

# Функція _create_telethon_sessions_table видаляється, оскільки таблиця створюється окремим SQL-скриптом

async def get_telethon_string_session(session_name: str) -> StringSession | None:
    """Отримує StringSession з БД за назвою сесії."""
    if not _session_pool:
        db_session_logger.error("Пул з'єднань з БД Telethon сесій не ініціалізовано.")
        return None
    async with _session_pool.acquire() as conn:
        # Використовуємо session_data TEXT з вашої DDL
        row = await conn.fetchrow('SELECT session_data FROM telethon_sessions WHERE session_name = $1', session_name)
        if row:
            db_session_logger.debug(f"Дані StringSession '{session_name}' знайдено у БД.")
            return StringSession(row['session_data']) # Створюємо StringSession з отриманого рядка
        db_session_logger.warning(f"Дані StringSession '{session_name}' не знайдено у БД.")
        return None

async def save_telethon_string_session(session_name: str, session_data: StringSession):
    """Зберігає або оновлює StringSession у БД."""
    if not _session_pool:
        db_session_logger.error("Пул з'єднань з БД Telethon сесій не ініціалізовано.")
        return
    async with _session_pool.acquire() as conn:
        # Зберігаємо StringSession як текст
        await conn.execute('''
            INSERT INTO telethon_sessions (session_name, session_data)
            VALUES ($1, $2)
            ON CONFLICT (session_name) DO UPDATE SET session_data = EXCLUDED.session_data, updated_at = CURRENT_TIMESTAMP
        ''', session_name, str(session_data)) # Перетворюємо StringSession на рядок
        db_session_logger.info(f"Дані StringSession '{session_name}' збережено/оновлено у БД.")

async def delete_telethon_string_session(session_name: str):
    """Видаляє дані Telethon сесії з БД."""
    if not _session_pool:
        db_session_logger.error("Пул з'єднань з БД Telethon сесій не ініціалізовано.")
        return
    async with _session_pool.acquire() as conn:
        await conn.execute('DELETE FROM telethon_sessions WHERE session_name = $1', session_name)
        db_session_logger.info(f"Дані сесії Telethon '{session_name}' видалено з БД.")