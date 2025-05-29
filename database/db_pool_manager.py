# database/db_pool_manager.py
import asyncpg
import logging
# Імпортуємо DATABASE_URL з config.py
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Змінна для зберігання пулу з'єднань
_db_pool = None

async def create_db_pool():
    """Створює пул з'єднань до бази даних PostgreSQL, використовуючи DATABASE_URL."""
    global _db_pool
    if _db_pool is None:
        try:
            # Використовуємо DATABASE_URL для створення пулу
            _db_pool = await asyncpg.create_pool(
                dsn=DATABASE_URL, # 'dsn' - це Connection string, яка приймає DATABASE_URL
                min_size=5,  # Мінімальна кількість з'єднань у пулі
                max_size=10, # Максимальна кількість з'єднань у пулі
                timeout=60   # Максимальний час очікування з'єднання
            )
            logger.info("Пул з'єднань до бази даних створено успішно.")
        except Exception as e:
            logger.critical(f"Помилка при створенні пулу з'єднань до бази даних: {e}", exc_info=True)
            raise # Повторно викидаємо виняток, щоб бот не запускався без БД

async def close_db_pool():
    """Закриває пул з'єднань до бази даних."""
    global _db_pool
    if _db_pool:
        logger.info("Закриття пулу з'єднань до бази даних...")
        await _db_pool.close()
        _db_pool = None
        logger.info("Пул з'єднань до бази даних закрито.")

async def get_db_pool():
    """Повертає існуючий пул з'єднань."""
    if _db_pool is None:
        logger.error("Пул з'єднань до бази даних не ініціалізовано. Викличте create_db_pool.")
        raise RuntimeError("Database pool not initialized.")
    return _db_pool