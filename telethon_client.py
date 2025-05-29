# telethon_client.py
import asyncio
import logging
from telethon.sync import TelegramClient
from telethon.sessions import MemorySession
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
from io import BytesIO
from telethon.crypto import AuthKey # Важливо: явно імпортуємо AuthKey для коректного типу

from config import API_ID, API_HASH, TELEGRAM_PHONE
from database import telethon_sessions_db # Імпортуємо модуль для роботи з сесіями в БД

logger = logging.getLogger(__name__)

class DBSession(MemorySession):
    """
    Кастомний клас сесії для Telethon, який зберігає дані у базі даних
    замість локального файлу.
    """
    def __init__(self, session_id=None):
        super().__init__() # Правильний виклик конструктора батьківського класу
        self.session_id = session_id # Може бути ім'я сесії, наприклад, 'refridex_main'
        self.db_pool = None # Пул БД буде встановлено пізніше
        self._loop = None # Посилання на asyncio event loop

    def set_db_pool(self, db_pool_instance):
        """Встановлює пул БД для використання в сесії."""
        self.db_pool = db_pool_instance
        # Важливо: отримати поточний loop, коли пул вже встановлений,
        # оскільки бот має запущений loop
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            # Це може статися, якщо loop ще не запущений (наприклад, при ініціалізації)
            # В такому випадку, loop буде встановлено пізніше, коли TelethonClientManager
            # буде підключений до основного loop aiogram.
            logger.debug("No running event loop found during DBSession init. Will try again later.")
            self._loop = None # Залишаємо None, якщо loop не знайдено

    async def load(self):
        """Завантажує дані сесії з БД."""
        if not self.db_pool:
            logger.warning("Database pool not set for DBSession. Cannot load session.")
            return

        session_data = await telethon_sessions_db.get_telethon_session(self.db_pool, self.session_id)
        if session_data:
            with BytesIO(session_data) as f:
                # Читаємо дані з BytesIO і присвоюємо їх внутрішнім атрибутам
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
            # Ініціалізуємо внутрішні атрибути для нової сесії
            self._dc_id = 1
            self._server_address = ""
            self._port = 443
            self._auth_key = AuthKey(b'\x00' * 256) # Новий AuthKey об'єкт
            self._time_offset = 0

    # ЗМІНЕНО: save() тепер синхронний
    def save(self):
        """
        Зберігає дані сесії у БД. Викликається Telethon синхронно.
        Асинхронна частина виконується у фоновому режимі.
        """
        if not self.db_pool:
            logger.warning("DB pool not set for DBSession. Cannot save session.")
            return
        
        # Перевірка, чи всі необхідні атрибути встановлені перед збереженням
        # _auth_key тепер об'єкт AuthKey, тому перевіряємо його тип
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
        # Використовуємо asyncio.create_task для запуску корутини в поточному циклі подій.
        # Це має працювати, оскільки бот вже має свій цикл подій.
        if self._loop and self._loop.is_running():
            asyncio.create_task(telethon_sessions_db.save_telethon_session(self.db_pool, self.session_id, session_data))
        else:
            logger.error(f"Cannot save session '{self.session_id}': No running event loop to schedule task.")


class TelethonClientManager:
    def __init__(self, db_pool, session_name='refridex_main'):
        self.db_pool = db_pool
        self.session_name = session_name
        self.client: TelegramClient = None
        self.session = DBSession(session_name)
        # Важливо: встановлюємо db_pool для сесії, що також встановлює loop
        self.session.set_db_pool(self.db_pool)

    async def start_client(self):
        """Ініціалізує та запускає Telethon клієнт."""
        if self.client and self.client.is_connected():
            logger.info("Telethon клієнт вже підключений.")
            return self.client

        # Завантажуємо сесію з БД перед створенням клієнта
        await self.session.load()

        self.client = TelegramClient(
            session=self.session, # Передаємо наш кастомний об'єкт сесії
            api_id=API_ID,
            api_hash=API_HASH,
            system_version="4.16.30-arm64-v8a", # Приклад system_version
            device_model="Xiaomi Redmi Note 13 Pro+", # Приклад device_model
            app_version="Refridex Bot 1.0"
        )

        try:
            # Спроба підключення без авторизації, якщо сесія вже є
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning("Telethon клієнт не авторизований. Потрібна авторизація.")
            else:
                logger.info(f"Telethon клієнт підключений та авторизований як @{(await self.client.get_me()).username}")

        except PhoneNumberUnoccupiedError:
            logger.critical(f"Номер телефону {TELEGRAM_PHONE} не зареєстрований в Telegram.")
            raise
        except Exception as e:
            logger.critical(f"Критична помилка при запуску Telethon клієнта: {e}", exc_info=True)
            raise

        return self.client

    async def disconnect_client(self):
        """Відключає Telethon клієнт."""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            logger.info("Telethon клієнт відключений.")

    async def authorize_client(self, phone_number=TELEGRAM_PHONE):
        """
        Запускає процес авторизації, надсилаючи код.
        Цей метод можна буде викликати з інтерфейсу бота.
        Повертає True, якщо код надіслано успішно.
        """
        if not self.client:
            raise RuntimeError("Telethon клієнт не ініціалізовано.")
        if await self.client.is_user_authorized():
            logger.info("Клієнт вже авторизований.")
            return True

        try:
            await self.client.send_code_request(phone_number)
            logger.info(f"Код авторизації надіслано на номер {phone_number}.")
            return True
        except Exception as e:
            logger.error(f"Помилка при відправці коду авторизації: {e}", exc_info=True)
            return False

    async def sign_in_client(self, code: str, password: str = None):
        """
        Завершує авторизацію за допомогою отриманого коду та, за необхідності, пароля 2FA.
        Цей метод також можна буде викликати з інтерфейсу бота.
        Повертає True, якщо авторизація успішна.
        """
        if not self.client:
            raise RuntimeError("Telethon клієнт не ініціалізовано.")
        try:
            if password:
                await self.client.sign_in(code=code, password=password)
            else:
                await self.client.sign_in(code=code)
            logger.info("Telethon клієнт успішно авторизований.")
            return True
        except SessionPasswordNeededError:
            logger.warning("Потрібен пароль двофакторної аутентифікації.")
            raise # Передаємо виняток, щоб викликаючий код міг його обробити
        except Exception as e:
            logger.error(f"Помилка при авторизації Telethon клієнта: {e}", exc_info=True)
            return False

    async def get_client(self) -> TelegramClient:
        """Повертає підключений Telethon клієнт."""
        if not self.client or not self.client.is_connected():
            logger.warning("Telethon клієнт не підключений, спроба перезапустити...")
            await self.start_client() # Спроба перезапустити, якщо не підключений
        return self.client