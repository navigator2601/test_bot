import asyncio
import logging
from typing import Dict, Any, Optional

from telethon import TelegramClient
from telethon.tl.types import User 
from telethon.sessions import StringSession 
from telethon.errors import SessionPasswordNeededError, FloodWaitError, AuthKeyUnregisteredError

# Імпортуємо ваш об'єкт конфігурації. 
# Переконайтеся, що 'config' має атрибути 'api_id', 'api_hash' (як SecretStr) та 'telegram_phone'.
from config import config 
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
            
            # Завантажуємо всі існуючі сесії з бази даних
            sessions_data = await self._get_all_sessions_from_db()

            if sessions_data:
                logger.info(f"Знайдено {len(sessions_data)} збережених сесій. Запускаємо їх...")
                for session_record in sessions_data:
                    phone_number = session_record['phone_number']
                    session_string = session_record['session_string']
                    # API ID та API Hash з БД можуть бути застарілими,
                    # краще завжди використовувати з конфігурації
                    
                    # API Hash має бути SecretStr
                    api_hash_value = config.api_hash.get_secret_value() if hasattr(config.api_hash, 'get_secret_value') else config.api_hash

                    # Створюємо клієнт для кожної знайденої сесії
                    client = TelegramClient(
                        session=StringSession(session_string),
                        api_id=config.api_id,
                        api_hash=api_hash_value
                    )
                    self.clients[phone_number] = client
                    logger.info(f"TelethonClientManager: Клієнт об'єкт для {phone_number} завантажено з БД.")
                    
                    # Створюємо задачу для підключення та авторизації
                    asyncio.create_task(self._run_client_and_authorize(phone_number, client, config.api_id, api_hash_value))
                    logger.info(f"Створено задачу для запуску та авторизації клієнта (з БД): {phone_number}")
            else:
                logger.info("Не знайдено збережених Telethon сесій у базі даних.")
                # Якщо немає збережених сесій, спробуйте запустити з номера з конфігурації
                phone_number_from_config = config.telegram_phone
                if phone_number_from_config:
                    # API Hash має бути SecretStr
                    api_hash_value = config.api_hash.get_secret_value() if hasattr(config.api_hash, 'get_secret_value') else config.api_hash
                    
                    # Створюємо новий клієнт без початкової сесії
                    client = TelegramClient(
                        session=StringSession(), # Порожня сесія для нового клієнта
                        api_id=config.api_id,
                        api_hash=api_hash_value
                    )
                    self.clients[phone_number_from_config] = client
                    logger.info(f"TelethonClientManager: Клієнт об'єкт для {phone_number_from_config} створено (нова сесія).")
                    asyncio.create_task(self._run_client_and_authorize(phone_number_from_config, client, config.api_id, api_hash_value))
                    logger.info(f"Створено задачу для запуску та авторизації клієнта (нова сесія): {phone_number_from_config}")
                else:
                    logger.warning("TELEGRAM_PHONE не встановлено в конфігурації і немає збережених сесій. Telethon клієнт не буде запущено.")
        else:
            logger.warning("Telethon клієнти вимкнено через конфігурацію.")

    async def _setup_client(self, phone_number: str):
        """
        Ця функція більше не потрібна як окремий виклик,
        оскільки логіка створення/завантаження та запуску клієнта перенесена в initialize().
        Її можна видалити або залишити закоментованою, якщо плануєте використовувати для індивідуального додавання клієнтів.
        Для поточних потреб initialize() є достатнім.
        """
        logger.warning(f"_setup_client викликано для {phone_number}, але ця функція застаріла. Використовуйте initialize().")
        # Якщо ви хочете додати клієнт вручну (наприклад, через адмін-панель), 
        # то ця логіка має бути винесена в окремий метод, який приймає phone_number, code, password
        pass 
        

    async def _initialize_client(self, phone_number: str, api_id: int, api_hash: str) -> TelegramClient:
        """
        Цей метод тепер є частиною логіки initialize(), 
        тому він більше не використовується напряму як окремий крок.
        Його можна видалити.
        """
        logger.warning(f"_initialize_client викликано для {phone_number}, але ця функція застаріла.")
        return TelegramClient(StringSession(), api_id, api_hash) # Повертаємо заглушку для компіляції, але метод слід видалити

    async def _run_client_and_authorize(self, phone_number: str, client: TelegramClient, api_id: int, api_hash: str):
        """Запускає клієнт Telethon та виконує авторизацію."""
        logger.info(f"Розпочинається авторизація для клієнта: {phone_number}")
        try:
            if not client.is_connected():
                await client.connect()
                logger.info(f"Клієнт {phone_number} підключено.")

            if not await client.is_user_authorized():
                logger.info(f"Клієнт {phone_number} не авторизовано. Запускаємо авторизацію...")
                try:
                    await client.start(phone=lambda: phone_number) # Передаємо функцію для отримання номера
                    logger.info(f"Код авторизації надіслано на {phone_number}. Перевірте Telegram.")
                    # Telethon автоматично запросить код та пароль у консолі
                    # Якщо ви хочете автоматично вводити код, вам потрібно буде створити функцію-хендлер
                    # для очікування вводу від користувача (наприклад, через Telegram-бота)
                    # і передавати його в client.start(code_callback=...)
                except FloodWaitError as e:
                    logger.error(f"FloodWaitError для {phone_number}: занадто багато запитів. Спробуйте пізніше. Чекайте {e.seconds} секунд.")
                    await asyncio.sleep(e.seconds + 5) # Чекаємо і спробуємо знову, або позначаємо як помилку
                    await self._run_client_and_authorize(phone_number, client, api_id, api_hash) # Рекурсивний виклик або альтернативна логіка
                    return
                except SessionPasswordNeededError:
                    logger.warning(f"Для {phone_number} потрібен двофакторний пароль. Будь ласка, введіть його в консолі, якщо бот зупинився.")
                    # Telethon запитає пароль в консолі. Якщо ви хочете автоматизувати, потрібно інтегрувати ввід через бота.
                except Exception as e:
                    logger.error(f"Помилка під час авторизації {phone_number}: {e}", exc_info=True)
                    await client.disconnect()
                    return

            # Після успішної авторизації, зберігаємо сесію
            if await client.is_user_authorized():
                await self._save_session_to_db(
                    phone_number=phone_number,
                    client=client, 
                    api_id=api_id,
                    api_hash=api_hash # Це може бути SecretStr, тому передаємо як є
                )
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
            # Для постійно працюючого бота, клієнт повинен залишатися підключеним, 
            # тому не викликаємо client.disconnect() тут.
            # Відключення відбувається тільки при завершенні роботи менеджера.
            pass

    async def _get_all_sessions_from_db(self) -> list[Dict[str, Any]]:
        """Отримує всі дані сесій з бази даних."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо отримати всі сесії.")
            return []
        
        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT phone_number, session_string, api_id, api_hash, last_login
                FROM telethon_sessions;
                """
            )
            return [dict(r) for r in records] # Перетворюємо записи в словники

    async def _get_session_from_db(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Отримує дані однієї сесії з бази даних за номером телефону."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо отримати сесію.")
            return None
        
        async with self.db_pool.acquire() as conn:
            session_str_row = await conn.fetchrow(
                """
                SELECT session_string, api_id, api_hash, last_login
                FROM telethon_sessions
                WHERE phone_number = $1;
                """,
                phone_number
            )
            return dict(session_str_row) if session_str_row else None


    async def _save_session_to_db(self, phone_number: str, client: TelegramClient, api_id: int, api_hash: Any):
        """Зберігає або оновлює дані сесії Telethon у базі даних."""
        if not self.db_pool:
            logger.error("DB pool не ініціалізовано, неможливо зберегти сесію.")
            return

        # Отримуємо session_string безпосередньо з об'єкта сесії клієнта
        session_string = client.session.save()
        if not session_string:
            logger.error(f"Отримана порожня session_string для {phone_number}. Неможливо зберегти сесію.")
            return
        
        # Перетворюємо SecretStr до str для збереження в БД, якщо це SecretStr
        api_hash_value = api_hash.get_secret_value() if hasattr(api_hash, 'get_secret_value') else api_hash

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO telethon_sessions (phone_number, session_string, api_id, api_hash, last_login)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (phone_number) DO UPDATE SET
                        session_string = EXCLUDED.session_string,
                        api_id = EXCLUDED.api_id,
                        api_hash = EXCLUDED.api_hash,
                        last_login = NOW();
                """, phone_number, session_string, api_id, api_hash_value)
            logger.info(f"Сесія Telethon для {phone_number} успішно збережена в БД.")
        except Exception as e:
            logger.error(f"Помилка при збереженні сесії Telethon для {phone_number} в БД: {e}", exc_info=True)

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
                try:
                    await client.disconnect()
                    logger.info(f"Клієнт {phone_number} відключено.")
                except Exception as e:
                    logger.error(f"Помилка при відключенні клієнта {phone_number}: {e}", exc_info=True)
            else:
                logger.info(f"Клієнт {phone_number} вже відключено.")
        self.clients.clear()

# Якщо TelethonClientManager використовується як частина aiogram startup/shutdown hooks
# то цей приклад буде адаптований до вашого main.py