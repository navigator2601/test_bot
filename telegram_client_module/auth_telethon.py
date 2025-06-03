# telegram_client_module/auth_telethon.py
import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import MemorySession
from telethon.errors import SessionPasswordNeededError
from io import BytesIO
from telethon.crypto import AuthKey # Важливо: явно імпортуємо AuthKey для коректного типу

from config import API_ID, API_HASH, TELEGRAM_PHONE, DATABASE_URL
from database.db_pool_manager import create_db_pool, get_db_pool, close_db_pool
from database.telethon_sessions_db import save_telethon_session, get_telethon_session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Починається виконання auth_telethon.py")

class TempDBSession(MemorySession):
    def __init__(self, session_id=None, db_pool_instance=None):
        super().__init__()
        self.session_id = session_id
        self.db_pool = db_pool_instance
        self._loop = None # Посилання на asyncio event loop

    async def load(self):
        if not self.db_pool:
            logger.warning("DB pool not set for TempDBSession. Cannot load session.")
            return

        session_data = await get_telethon_session(self.db_pool, self.session_id)
        if session_data:
            with BytesIO(session_data) as f:
                dc_id_bytes = f.read(1)
                if not dc_id_bytes:
                    logger.warning(f"Empty or incomplete session data for '{self.session_id}'. Not loading.")
                    return
                self._dc_id = int.from_bytes(dc_id_bytes, 'big')

                address_len_bytes = f.read(1)
                if not address_len_bytes:
                    logger.warning(f"Incomplete session data (address_len) for '{self.session_id}'. Not loading.")
                    return
                address_len = address_len_bytes[0]
                self._server_address = f.read(address_len).decode('utf-8')

                port_bytes = f.read(2)
                if not port_bytes:
                    logger.warning(f"Incomplete session data (port) for '{self.session_id}'. Not loading.")
                    return
                self._port = int.from_bytes(port_bytes, 'big')

                auth_key_bytes = f.read(256)
                if not auth_key_bytes or len(auth_key_bytes) != 256:
                    logger.warning(f"Incomplete auth_key data for '{self.session_id}'. Not loading.")
                    return
                self._auth_key = AuthKey(auth_key_bytes) # Перетворюємо байти на об'єкт AuthKey

                time_offset_bytes = f.read(4)
                if not time_offset_bytes:
                    logger.warning(f"Incomplete time_offset data for '{self.session_id}'. Not loading.")
                    return
                self._time_offset = int.from_bytes(time_offset_bytes, 'big', signed=True)
        else:
            logger.info(f"Сесія '{self.session_id}' не знайдена в БД. Буде створена нова.")
            self._dc_id = 1
            self._server_address = ""
            self._port = 443
            self._auth_key = AuthKey(b'\x00' * 256) # Новий AuthKey об'єкт
            self._time_offset = 0

    # ЗМІНЕНО: save() тепер синхронний
    def save(self):
        if not self.db_pool:
            logger.warning("DB pool not set for TempDBSession. Cannot save session.")
            return

        # Важливо: встановлюємо _loop тут, оскільки auth_telethon.py запускається без aiogram
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                logger.error("No running event loop found during TempDBSession.save. Cannot save session asynchronously.")
                return

        # Перевірка, чи всі необхідні атрибути встановлені перед збереженням
        if not all([isinstance(self._dc_id, int),
                    isinstance(self._server_address, str),
                    isinstance(self._port, int),
                    isinstance(self._auth_key, AuthKey) and len(self._auth_key.key) == 256,
                    isinstance(self._time_offset, int)]):
             logger.warning(f"Skipping save for session '{self.session_id}': Incomplete session attributes.")
             return

        with BytesIO() as f:
            f.write(self._dc_id.to_bytes(1, 'big'))
            address_bytes = self._server_address.encode('utf-8')
            f.write(len(address_bytes).to_bytes(1, 'big'))
            f.write(address_bytes)
            f.write(self._port.to_bytes(2, 'big'))
            f.write(self._auth_key.key) # Використовуємо .key для отримання байтів з об'єкта AuthKey
            f.write(self._time_offset.to_bytes(4, 'big', signed=True))
            session_data = f.getvalue()

        # Запускаємо асинхронну операцію збереження у фоновому режимі
        # Використовуємо asyncio.create_task, оскільки auth_telethon.py має працюючий loop
        if self._loop and self._loop.is_running():
            asyncio.create_task(save_telethon_session(self.db_pool, self.session_id, session_data))
        else:
            logger.error(f"Cannot save session '{self.session_id}': No running event loop to schedule task.")


async def run_auth():
    logger.info("Виконується функція run_auth().")
    client = None # Ініціалізуємо client перед try блоком
    db_pool = None # Ініціалізуємо db_pool перед try блоком
    try:
        await create_db_pool()
        db_pool = await get_db_pool()
        session_name = 'refridex_main'

        session = TempDBSession(session_name, db_pool)
        # Встановлюємо db_pool для сесії, що також встановлює loop
        # Це потрібно викликати тут, бо db_pool стає доступним лише після create_db_pool
        session.db_pool = db_pool
        try:
            session._loop = asyncio.get_event_loop()
        except RuntimeError:
            logger.warning("No running event loop found when setting _loop in auth_telethon. Will rely on client.connect to start it.")
            # Це нормально, якщо loop ще не запущений, Telethon Client сам його запустить

        await session.load() # Тепер з await

        client = TelegramClient(
            session=session,
            api_id=API_ID,
            api_hash=API_HASH,
            system_version="4.16.30-arm64-v8a",
            device_model="Xiaomi Redmi Note 13 Pro+",
            app_version="Refridex Bot 1.0"
        )

        logger.info("Telethon клієнт ініціалізовано. Спроба підключення...")
        await client.connect()

        if not await client.is_user_authorized():
            logger.info(f"Спроба авторизації для {TELEGRAM_PHONE}...")
            try:
                await client.send_code_request(TELEGRAM_PHONE)
                code = input('Введіть код з Telegram: ')
                await client.sign_in(TELEGRAM_PHONE, code)
            except SessionPasswordNeededError:
                password = input('Введіть пароль двофакторної аутентифікації: ')
                await client.sign_in(password=password)
            except Exception as e:
                logger.error(f"Помилка авторизації: {e}", exc_info=True)
                return # Завершуємо функцію при помилці авторизації

        me = await client.get_me()
        logger.info(f"Авторизація успішна! Користувач: {me.username or me.first_name}")

    except Exception as e:
        logger.error(f"Критична помилка під час виконання run_auth(): {e}", exc_info=True)
    finally:
        if client and client.is_connected():
            await client.disconnect() # При відключенні Telethon клієнт викликає session.save()
        if db_pool: # Закриваємо пул тільки якщо він був успішно створений
            await close_db_pool()
        logger.info("Telethon авторизаційний скрипт завершено.")

if __name__ == '__main__':
    logger.info("Блок if __name__ == '__main__': виконується.")
    try:
        asyncio.run(run_auth())
    except Exception as e:
        logger.critical(f"Критична помилка при запуску asyncio.run: {e}", exc_info=True)