# telegram_client_module/telethon_client.py

import asyncio
import logging
from typing import Optional # Імпортуємо Optional для анотацій типів

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User as TelethonUser # Щоб уникнути конфлікту імен, якщо потрібно в іншому місці
import asyncpg # <--- ЦЕ КЛЮЧОВА ЗМІНА: імпортуємо asyncpg напряму

logger = logging.getLogger(__name__)

class TelethonClientManager:
    def __init__(self, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.clients: dict[str, TelegramClient] = {} # Зберігає клієнти за номером телефону
        logger.info("TelethonClientManager ініціалізовано.")

    async def initialize(self, db_pool: asyncpg.Pool): # <--- ЗМІНЕНО ТИП НА asyncpg.Pool
        """Завантажує та запускає збережені сесії з бази даних."""
        logger.info("Спроба запуску Telethon клієнтів...")
        sessions = await db_pool.fetch("SELECT phone_number, session_string FROM telethon_sessions")
        
        if not sessions:
            logger.info("Не знайдено збережених сесій.")
            return

        logger.info(f"Знайдено {len(sessions)} збережених сесій. Запускаємо їх...")
        
        for record in sessions:
            phone_number = record['phone_number']
            session_string = record['session_string']
            
            try:
                # Відновлюємо клієнта з StringSession
                client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
                self.clients[phone_number] = client # Додаємо клієнта до менеджера
                logger.info(f"TelethonClientManager: Об'єкт клієнта для {phone_number} завантажено з БД.")
                
                # Запускаємо клієнта в окремій задачі, щоб не блокувати запуск бота
                asyncio.create_task(self._start_and_authorize_client(phone_number, client, db_pool))
                logger.info(f"Створено задачу для запуску та авторизації клієнта (з БД): {phone_number}")

            except Exception as e:
                logger.error(f"Помилка при завантаженні або запуску сесії для {phone_number}: {e}", exc_info=True)

    async def _start_and_authorize_client(self, phone_number: str, client: TelegramClient, db_pool: asyncpg.Pool): # <--- ЗМІНЕНО ТИП
        """Внутрішня функція для підключення та авторизації клієнта."""
        try:
            logger.info(f"Розпочинається авторизація для клієнта: {phone_number}")
            if not client.is_connected():
                await client.connect()
                logger.info(f"Клієнт {phone_number} підключено.")

            if not await client.is_user_authorized():
                logger.warning(f"Клієнт {phone_number} не авторизований після підключення. Можливо, сесія недійсна.")
                await self.delete_session(phone_number, db_pool)
                self.clients.pop(phone_number, None)
                return

            session_string = client.session.save()
            await self.save_session_to_db(phone_number, client, db_pool)
            me = await client.get_me()
            logger.info(f"Клієнт {phone_number} успішно авторизовано та збережено сесію. Увійшов як: {me.first_name} (@{me.username or 'N/A'}); ID: {me.id}")

        except Exception as e:
            logger.error(f"Помилка авторизації клієнта {phone_number}: {e}", exc_info=True)
            await self.delete_session(phone_number, db_pool)
            self.clients.pop(phone_number, None)

    def get_client(self, phone_number: str) -> Optional[TelegramClient]:
        """Повертає клієнта за номером телефону, якщо він існує."""
        return self.clients.get(phone_number)

    def add_client(self, phone_number: str, client: TelegramClient):
        """Додає або оновлює клієнта в менеджері."""
        self.clients[phone_number] = client

    def get_all_active_clients(self) -> dict[str, TelegramClient]:
        """Повертає словник усіх активних (завантажених) клієнтів."""
        return self.clients

    async def save_session_to_db(self, phone_number: str, client: TelegramClient, db_pool: asyncpg.Pool): # <--- ЗМІНЕНО ТИП
        """Зберігає або оновлює сесію клієнта в базі даних."""
        session_string = client.session.save()
        await db_pool.execute(
            """
            INSERT INTO telethon_sessions (phone_number, session_string)
            VALUES ($1, $2)
            ON CONFLICT (phone_number) DO UPDATE SET session_string = $2;
            """,
            phone_number,
            session_string
        )
        logger.info(f"Сесія Telethon для {phone_number} успішно збережена в БД.")

    async def load_session_from_db(self, phone_number: str, db_pool: asyncpg.Pool) -> Optional[str]: # <--- ЗМІНЕНО ТИП
        """Завантажує рядок сесії з бази даних."""
        record = await db_pool.fetchrow(
            "SELECT session_string FROM telethon_sessions WHERE phone_number = $1;",
            phone_number
        )
        return record['session_string'] if record else None

    async def delete_session(self, phone_number: str, db_pool: asyncpg.Pool): # <--- ЗМІНЕНО ТИП
        """Видаляє сесію з бази даних."""
        await db_pool.execute(
            "DELETE FROM telethon_sessions WHERE phone_number = $1;",
            phone_number
        )
        logger.info(f"Сесія Telethon для {phone_number} видалена з БД.")

    async def shutdown_all_clients(self):
        """Відключає всі активні клієнти."""
        for phone_number, client in list(self.clients.items()):
            if client.is_connected():
                try:
                    await client.disconnect()
                    logger.info(f"Клієнт Telethon для {phone_number} відключено.")
                except Exception as e:
                    logger.error(f"Помилка відключення клієнта {phone_number}: {e}", exc_info=True)
            self.clients.pop(phone_number, None)
        logger.info("Усі Telethon клієнти відключено.")