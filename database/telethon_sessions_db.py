# database/telethon_sessions_db.py
import asyncpg # <-- ДОДАТИ ЦЕЙ РЯДОК
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def create_telethon_sessions_table(pool: asyncpg.Pool):
    """
    Перевіряє або створює таблицю telethon_sessions, використовуючи вашу структуру.
    Зауваження: Якщо таблиця вже існує з іншою структурою, цей CREATE TABLE IF NOT EXISTS
    не змінить її. Переконайтеся, що ваша існуюча таблиця має потрібні стовпці.
    """
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS telethon_sessions (
                    phone_number VARCHAR(255) PRIMARY KEY,
                    session_string TEXT NOT NULL,
                    api_id INT NOT NULL,
                    api_hash VARCHAR(255) NOT NULL,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL -- Використовуємо вашу існуючу структуру
                );
            """)
            logger.info("Таблиця 'telethon_sessions' перевірена/створена з ВАШОЮ структурою.")

            # Тригер для оновлення last_login (якщо це ваш аналог updated_at)
            if isinstance(pool, asyncpg.pool.Pool):
                # Видаляємо старий тригер/функцію, щоб уникнути конфліктів, якщо вони існували
                await conn.execute("""
                    DROP TRIGGER IF EXISTS set_last_login_telethon_sessions ON telethon_sessions;
                    DROP FUNCTION IF EXISTS update_last_login_column() CASCADE; -- CASCADE для видалення залежних об'єктів
                """)
                logger.debug("Видалено старий тригер/функцію last_login (якщо існували).")

                # Тепер створюємо функцію та тригер для last_login
                await conn.execute("""
                    CREATE OR REPLACE FUNCTION update_last_login_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.last_login = NOW();
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_last_login_telethon_sessions') THEN
                            CREATE TRIGGER set_last_login_telethon_sessions
                            BEFORE UPDATE ON telethon_sessions
                            FOR EACH ROW
                            EXECUTE FUNCTION update_last_login_column();
                        END IF;
                    END $$;
                """)
                logger.info("Тригер 'set_last_login_telethon_sessions' перевірений/створений (для PostgreSQL).")

        except Exception as e:
            logger.error(f"Помилка при створенні/перевірці таблиці 'telethon_sessions': {e}", exc_info=True)
            raise

async def save_telethon_session(db_pool: asyncpg.Pool, phone_number: str, session_data_bytes: bytes, api_id: int, api_hash: str):
    """
    Зберігає або оновлює дані сесії Telethon у базу даних.
    Використовує phone_number як первинний ключ.
    session_data_bytes має бути bytes (серіалізована сесія).
    """
    session_string = session_data_bytes.decode('utf-8')
    current_time = datetime.now() # ЗМІНА ТУТ: Без timezone.utc для відповідності TIMESTAMP WITHOUT TIME ZONE

    async with db_pool.acquire() as conn:
        try:
            await conn.execute(
                """
                INSERT INTO telethon_sessions (phone_number, session_string, api_id, api_hash, last_login)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (phone_number) DO UPDATE SET
                    session_string = EXCLUDED.session_string,
                    api_id = EXCLUDED.api_id,
                    api_hash = EXCLUDED.api_hash,
                    last_login = EXCLUDED.last_login;
                """,
                phone_number,
                session_string,
                api_id,
                api_hash,
                current_time
            )
            logger.info(f"Сесію Telethon для '{phone_number}' збережено/оновлено в БД.")
        except Exception as e:
            logger.error(f"Помилка при збереженні сесії Telethon для '{phone_number}': {e}", exc_info=True)
            raise

async def get_telethon_session(db_pool: asyncpg.Pool, phone_number: str) -> bytes | None:
    """
    Отримує дані сесії Telethon з бази даних за номером телефону.
    Повертає bytes (декодовані з session_string) або None.
    """
    async with db_pool.acquire() as conn:
        try:
            record = await conn.fetchrow(
                "SELECT session_string, api_id, api_hash FROM telethon_sessions WHERE phone_number = $1",
                phone_number
            )
            if record:
                session_string = record['session_string']
                logger.info(f"Сесію Telethon для '{phone_number}' завантажено з БД.")
                return session_string.encode('utf-8')
            else:
                logger.info(f"Сесію Telethon для '{phone_number}' не знайдено в БД.")
                return None
        except Exception as e:
            logger.error(f"Помилка при отриманні сесії Telethon для '{phone_number}': {e}", exc_info=True)
            raise

async def delete_telethon_session(db_pool: asyncpg.Pool, phone_number: str):
    """
    Видаляє сесію Telethon з бази даних за номером телефону.
    """
    async with db_pool.acquire() as conn:
        try:
            await conn.execute(
                "DELETE FROM telethon_sessions WHERE phone_number = $1",
                phone_number
            )
            logger.info(f"Сесію Telethon для '{phone_number}' видалено з БД.")
        except Exception as e:
            logger.error(f"Помилка при видаленні сесії Telethon для '{phone_number}': {e}", exc_info=True)
            raise