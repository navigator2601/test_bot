import asyncio
import logging
from typing import Dict, Any, Optional

from telethon import TelegramClient
from telethon.tl.types import User # Якщо ви використовуєте User, переконайтесь, що він імпортований
from telethon.sessions import StringSession # <--- НОВЕ: Імпорт StringSession
from telethon.errors import SessionPasswordNeededError, FloodWaitError, AuthKeyUnregisteredError

from config import config # Імпортуємо ваш об'єкт конфігурації
from database.db_pool_manager import get_db_pool # Імпорт для доступу до пулу БД

logger = logging.getLogger(__name__)

class TelethonClientManager:
    """
    Керує життєвим циклом Telethon клієнтів, включаючи авторизацію та зберігання сесій у БД.
    """
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.db_pool = None # Пул бази даних буде ініціалізовано пізніше
        logger.info("TelethonClientManager ініціалізовано.")

    async def initialize(self):
        """Ініціалізує пул бази даних та завантажує/запускає клієнтів."""
        self.db_pool = await get_db_pool()
        if not self.db_pool:
            logger.critical("Пул бази даних не ініціалізовано. Неможливо запустити Telethon клієнтів.")
            return

        if config.telethon_client_enabled:
            logger.info("Спроба запуску Telethon клієнтів...")
            # Запускаємо клієнт для кожного сконфігурованого номера телефону
            # Наразі у нас лише один номер з .env
            phone_number = config.telegram_phone
            if phone_number:
                await self._setup_client(phone_number)
            else:
                logger.warning("TELEGRAM_PHONE не встановлено в конфігурації. Telethon клієнт не буде запущено.")
        else:
            logger.warning("Telethon клієнти вимкнено через конфігурацію.")

    async def _setup_client(self, phone_number: str):
        """Створює та налаштовує один Telethon клієнт."""
        api_id = config.api_id
        api_hash = config.api_hash

        if not api_id or not api_hash:
            logger.error(f"API_ID або API_HASH відсутні для {phone_number}. Клієнт не буде запущено.")
            return

        client = await self._initialize_client(phone_number, api_id, api_hash)
        self.clients[phone_number] = client
        logger.info(f"TelethonClientManager: Клієнт об'єкт для {phone_number} створено.")

        # Створюємо задачу для запуску та авторизації клієнта
        asyncio.create_task(self._run_client_and_authorize(phone_number, client, api_id, api_hash))
        logger.info(f"Створено задачу для запуску та авторизації клієнта: {phone_number}")


    async def _initialize_client(self, phone_number: str, api_id: int, api_hash: str) -> TelegramClient:
        """
        Ініціалізує об'єкт TelegramClient, завантажуючи існуючу сесію або створюючи нову.
        """
        # <--- ПОЧАТОК ЗМІН В _initialize_client ---
        session_string = None
        session_data = await self._get_session_from_db(phone_number)
        if session_data:
            session_string = session_data['session_string']

        # Створюємо TelegramClient, використовуючи StringSession
        # Якщо session_string є, Telethon спробує завантажити сесію з нього.
        # Якщо ні, створиться нова порожня сесія.
        client = TelegramClient(
            session=StringSession(session_string) if session_string else StringSession(),
            api_id=api_id,
            api_hash=api_hash
        )
        # <--- КІНЕЦЬ ЗМІН В _initialize_client ---
        return client

    async def _run_client_and_authorize(self, phone_number: str, client: TelegramClient, api_id: int, api_hash: str):
        """Запускає клієнт Telethon та виконує авторизацію."""
        logger.info(f"Розпочинається авторизація для клієнта: {phone_number}")
        try:
            await client.connect()
            logger.info(f"Клієнт {phone_number} підключено.")

            if not await client.is_user_authorized():
                logger.info(f"Клієнт {phone_number} не авторизовано. Запускаємо авторизацію...")
                try:
                    await client.start(phone=lambda: phone_number) # Передаємо функцію для отримання номера
                    logger.info(f"Код авторизації надіслано на {phone_number}. Перевірте Telegram.")
                    # Telethon автоматично запросить код та пароль у консолі
                except FloodWaitError as e:
                    logger.error(f"FloodWaitError для {phone_number}: занадто багато запитів. Спробуйте пізніше. Чекайте {e.seconds} секунд.")
                    # Можете додати тут логіку для очікування
                except SessionPasswordNeededError:
                    logger.warning(f"Для {phone_number} потрібен двофакторний пароль.")
                    # Telethon запитає пароль в консолі, якщо не було передано password=...
                except Exception as e:
                    logger.error(f"Помилка під час авторизації {phone_number}: {e}", exc_info=True)
                    await client.disconnect()
                    return

            # Після успішної авторизації, зберігаємо сесію
            if await client.is_user_authorized():
                # <--- ПОЧАТОК ЗМІН У _save_session_to_db виклику ---
                await self._save_session_to_db(
                    phone_number=phone_number,
                    client=client, # <--- Тепер передаємо об'єкт client
                    api_id=api_id,
                    api_hash=api_hash
                )
                # <--- КІНЕЦЬ ЗМІН У _save_session_to_db виклику ---
                logger.info(f"Клієнт {phone_number} успішно авторизовано та збережено сесію.")
                # Отримання інформації про користувача після авторизації
                me: User = await client.get_me()
                logger.info(f"Увійшов як: {me.first_name} (@{me.username or 'N/A'}); ID: {me.id}")
            else:
                logger.error(f"Клієнт {phone_number} не вдалося авторизувати після спроби.")

        except AuthKeyUnregisteredError:
            logger.error(f"Помилка AuthKeyUnregisteredError для {phone_number}. Можливо, сесія недійсна. Видалення сесії з БД.")
            await self._delete_session_from_db(phone_number)
            # Можете спробувати перезапустити авторизацію або повідомити адміністратора
        except Exception as e:
            logger.error(f"Загальна помилка запуску/авторизації клієнта {phone_number}: {e}", exc_info=True)
        finally:
            # Важливо: відключайте клієнт, коли він не потрібен або при завершенні роботи
            # Для постійно працюючого бота, відключення може бути не відразу після авторизації
            # але при завершенні роботи програми.
            pass

    async def _get_session_from_db(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Отримує дані сесії з бази даних за номером телефону."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо отримати сесію.")
            return None
        async with self.db_pool.acquire() as conn:
            # <--- ЗМІНИ ТУТ: Використовуємо 'session_string' та 'last_login' ---
            session_str_row = await conn.fetchrow(
                """
                SELECT session_string, api_id, api_hash, last_login
                FROM telethon_sessions
                WHERE phone_number = $1;
                """,
                phone_number
            )
            # <--- КІНЕЦЬ ЗМІН ---
            return session_str_row

    # <--- ПОЧАТОК ЗМІН В _save_session_to_db ---
    async def _save_session_to_db(self, phone_number: str, client: TelegramClient, api_id: int, api_hash: str):
        """Зберігає або оновлює дані сесії Telethon у базі даних."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо зберегти сесію.")
            return

        # Отримуємо session_string безпосередньо з об'єкта сесії клієнта
        # Це критично важливий крок, який генерує рядок сесії для зберігання.
        session_string = client.session.save()
        if not session_string:
            logger.error(f"Отримана порожня session_string для {phone_number}. Неможливо зберегти сесію.")
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO telethon_sessions (phone_number, session_string, api_id, api_hash, last_login)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (phone_number) DO UPDATE SET
                        session_string = EXCLUDED.session_string,
                        api_id = EXCLUDED.api_id,
                        api_hash = EXCLUDED.api_hash,
                        last_login = NOW(); -- Тепер стовпець називається last_login
                """, phone_number, session_string, api_id, api_hash)
            logger.info(f"Сесія Telethon для {phone_number} успішно збережена в БД.")
        except Exception as e:
            logger.error(f"Помилка при збереженні сесії Telethon для {phone_number} в БД: {e}", exc_info=True)
    # <--- КІНЕЦЬ ЗМІН ---

    async def _delete_session_from_db(self, phone_number: str):
        """Видаляє дані сесії з бази даних за номером телефону."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо видалити сесію.")
            return
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM telethon_sessions WHERE phone_number = $1;",
                phone_number
            )
        logger.info(f"Сесія Telethon для {phone_number} видалена з БД.")

    async def shutdown(self):
        """Коректно відключає всі Telethon клієнти."""
        logger.info("Завершення роботи TelethonClientManager. Відключення клієнтів...")
        for phone_number, client in self.clients.items():
            if client.is_connected():
                await client.disconnect()
                logger.info(f"Клієнт {phone_number} відключено.")
        self.clients.clear()

# Якщо TelethonClientManager використовується як частина aiogram startup/shutdown hooks
# то цей приклад буде адаптований до вашого main.py