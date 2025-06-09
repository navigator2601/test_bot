# database/telethon_chats_db.py
import asyncpg
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

async def add_allowed_chat(
    db_pool: asyncpg.Pool,
    chat_id: int,
    chat_title: Optional[str] = None,
    added_by_user_id: Optional[int] = None
) -> bool:
    """
    Додає ID чату до списку дозволених Telethon чатів.
    Повертає True, якщо чат було додано, False, якщо він вже існував.
    """
    try:
        query = """
            INSERT INTO telethon_allowed_chats (chat_id, chat_title, added_by_user_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (chat_id) DO NOTHING
            RETURNING id;
        """
        res = await db_pool.fetchval(query, chat_id, chat_title, added_by_user_id)
        if res:
            logger.info(f"Чат ID {chat_id} ('{chat_title}') додано до дозволених Telethon чатів.")
            return True
        else:
            logger.info(f"Чат ID {chat_id} ('{chat_title}') вже існує у дозволених Telethon чатах.")
            return False
    except Exception as e:
        logger.error(f"Помилка при додаванні чату {chat_id} до дозволених: {e}", exc_info=True)
        return False

async def remove_allowed_chat(db_pool: asyncpg.Pool, chat_id: int) -> bool:
    """
    Видаляє ID чату зі списку дозволених Telethon чатів.
    Повертає True, якщо чат було видалено, False, якщо його не існувало.
    """
    try:
        query = """
            DELETE FROM telethon_allowed_chats
            WHERE chat_id = $1
            RETURNING id;
        """
        res = await db_pool.fetchval(query, chat_id)
        if res:
            logger.info(f"Чат ID {chat_id} видалено зі списку дозволених Telethon чатів.")
            return True
        else:
            logger.info(f"Чат ID {chat_id} не знайдено у дозволених Telethon чатах.")
            return False
    except Exception as e:
        logger.error(f"Помилка при видаленні чату {chat_id} зі списку дозволених: {e}", exc_info=True)
        return False

async def get_all_allowed_chats(db_pool: asyncpg.Pool) -> List[Tuple[int, Optional[str]]]:
    """
    Отримує список всіх дозволених Telethon чатів.
    Повертає список кортежів (chat_id, chat_title).
    """
    try:
        query = "SELECT chat_id, chat_title FROM telethon_allowed_chats ORDER BY chat_title ASC NULLS LAST;"
        rows = await db_pool.fetch(query)
        return [(r['chat_id'], r['chat_title']) for r in rows]
    except Exception as e:
        logger.error(f"Помилка при отриманні списку дозволених Telethon чатів: {e}", exc_info=True)
        return []

async def is_chat_allowed(db_pool: asyncpg.Pool, chat_id: int) -> bool:
    """
    Перевіряє, чи є чат з даним ID у списку дозволених.
    """
    try:
        query = "SELECT EXISTS (SELECT 1 FROM telethon_allowed_chats WHERE chat_id = $1);"
        exists = await db_pool.fetchval(query, chat_id)
        return exists
    except Exception as e:
        logger.error(f"Помилка при перевірці дозволеного чату {chat_id}: {e}", exc_info=True)
        return False