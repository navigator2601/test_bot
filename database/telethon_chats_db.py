# database/telethon_chats_db.py
import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def create_telethon_allowed_chats_table(conn: asyncpg.Connection):
    """Створює таблицю 'telethon_allowed_chats', якщо її не існує, з оновленими полями."""
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS telethon_allowed_chats (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL UNIQUE,
            chat_title TEXT,
            chat_type TEXT, -- НОВЕ ПОЛЕ
            username TEXT,  -- НОВЕ ПОЛЕ
            added_by_user_id BIGINT,
            added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    logger.info("Таблиця 'telethon_allowed_chats' перевірена/створена (з полями chat_type та username).")

async def add_telethon_allowed_chat(
    pool: asyncpg.Pool, 
    chat_id: int, 
    chat_title: str, 
    chat_type: Optional[str], 
    username: Optional[str],  
    added_by_user_id: int
) -> bool:
    """Додає дозволений чат до таблиці telethon_allowed_chats з типом та юзернеймом.
    
    Повертає True у разі успіху, False, якщо чат вже існує або виникла помилка.
    """
    try:
        # ON CONFLICT (chat_id) DO NOTHING - дозволяє уникнути помилки, якщо чат вже є
        result = await pool.execute(
            '''
            INSERT INTO telethon_allowed_chats (chat_id, chat_title, chat_type, username, added_by_user_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (chat_id) DO NOTHING
            ''',
            chat_id, chat_title, chat_type, username, added_by_user_id
        )
        # 'INSERT 0 1' означає, що 1 рядок було вставлено. 'INSERT 0 0' означає, що рядок не було вставлено (через ON CONFLICT)
        if result == 'INSERT 0 1':
            logger.info(f"Чат '{chat_title}' (ID: {chat_id}, Type: {chat_type}, Username: {username}) успішно додано до telethon_allowed_chats.")
            return True
        else:
            logger.warning(f"Чат '{chat_title}' (ID: {chat_id}) вже існує в telethon_allowed_chats (або не було додано).")
            return False
    except Exception as e:
        logger.error(f"Помилка при додаванні чату '{chat_title}' (ID: {chat_id}) до telethon_allowed_chats: {e}", exc_info=True)
        return False

async def get_all_telethon_allowed_chats(pool: asyncpg.Pool) -> list[dict]:
    """Повертає всі дозволені чати з БД, включаючи тип та юзернейм."""
    try:
        records = await pool.fetch("SELECT * FROM telethon_allowed_chats ORDER BY added_at DESC")
        return [dict(r) for r in records]
    except Exception as e:
        logger.error(f"Помилка при отриманні дозволених чатів з БД: {e}", exc_info=True)
        return []

# --- НОВА ФУНКЦІЯ: get_telethon_allowed_chat_by_id ---
async def get_telethon_allowed_chat_by_id(pool: asyncpg.Pool, chat_id: int) -> Optional[dict]:
    """
    Отримує інформацію про дозволений чат з БД за його chat_id.
    Повертає словник з даними чату або None, якщо чат не знайдено.
    """
    try:
        record = await pool.fetchrow(
            "SELECT chat_id, chat_title, chat_type, username, added_by_user_id, added_at FROM telethon_allowed_chats WHERE chat_id = $1",
            chat_id
        )
        if record:
            return dict(record)
        return None
    except Exception as e:
        logger.error(f"Помилка при отриманні дозволеного чату з ID {chat_id} з БД: {e}", exc_info=True)
        return None

async def delete_telethon_allowed_chat(pool: asyncpg.Pool, chat_id: int) -> bool:
    """Видаляє дозволений чат з БД за chat_id."""
    try:
        result = await pool.execute(
            "DELETE FROM telethon_allowed_chats WHERE chat_id = $1",
            chat_id
        )
        if result == "DELETE 1":
            logger.info(f"Чат з ID {chat_id} успішно видалено з telethon_allowed_chats.")
            return True
        else:
            logger.warning(f"Чат з ID {chat_id} не знайдено в telethon_allowed_chats для видалення.")
            return False
    except Exception as e:
        logger.error(f"Помилка при видаленні чату з ID {chat_id} з telethon_allowed_chats: {e}", exc_info=True)
        return False