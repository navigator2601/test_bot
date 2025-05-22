# telethon_client.py
from telethon.sync import TelegramClient
from config import API_ID, API_HASH, TELEGRAM_PHONE, TELETHON_SESSION_NAME
import logging
import asyncio

telethon_logger = logging.getLogger(__name__)

# Глобальна змінна для клієнта Telethon та блокування
_telethon_client = None
_telethon_lock = asyncio.Lock() # Для безпечного доступу до клієнта

# Callback-функції, які будуть встановлюватися ззовні (з обробника aiogram)
_code_request_callback = None
_password_request_callback = None

def set_auth_callbacks(code_callback, password_callback):
    """Встановлює колбек-функції для запиту коду та паролю."""
    global _code_request_callback, _password_request_callback
    _code_request_callback = code_callback
    _password_request_callback = password_callback

async def _request_code_callback():
    """Колбек для запиту коду авторизації (буде викликатися Telethon)."""
    if _code_request_callback:
        telethon_logger.debug("Викликано _request_code_callback. Делегуємо запит боту.")
        return await _code_request_callback()
    else:
        telethon_logger.error("Колбек для запиту коду не встановлено! Неможливо авторизувати Telethon.")
        raise ConnectionError("Колбек для запиту коду не встановлено.")

async def _request_password_callback():
    """Колбек для запиту паролю двохетапної перевірки (буде викликатися Telethon)."""
    if _password_request_callback:
        telethon_logger.debug("Викликано _request_password_callback. Делегуємо запит боту.")
        return await _password_request_callback()
    else:
        telethon_logger.error("Колбек для запиту паролю не встановлено! Неможливо авторизувати Telethon.")
        raise ConnectionError("Колбек для запиту паролю не встановлено.")

async def get_telethon_client_instance() -> TelegramClient | None:
    """
    Повертає ініціалізований Telethon клієнт.
    Виконує авторизацію, якщо клієнт ще не авторизований.
    """
    global _telethon_client

    async with _telethon_lock:
        if _telethon_client is None:
            telethon_logger.info("Ініціалізація нового Telethon клієнта.")
            try:
                _telethon_client = TelegramClient(
                    TELETHON_SESSION_NAME,
                    API_ID,
                    API_HASH,
                    system_version="4.16.30-vx" # Рекомендовано для коректної роботи
                )
                await _telethon_client.connect()
                telethon_logger.info("Telethon клієнт підключено.")

                if not await _telethon_client.is_user_authorized():
                    telethon_logger.warning("Telethon клієнт не авторизований. Запускаємо процес авторизації.")
                    try:
                        # Тут ми передаємо наші кастомні колбеки
                        await _telethon_client.start(
                            phone=TELEGRAM_PHONE,
                            code_callback=_request_code_callback,
                            password_callback=_request_password_callback,
                            qr_callback=None # Можна додати обробку QR, якщо потрібно
                        )
                        telethon_logger.info("Telethon клієнт успішно авторизований.")
                    except Exception as e:
                        telethon_logger.error(f"Помилка авторизації Telethon: {e}", exc_info=True)
                        await _telethon_client.disconnect()
                        _telethon_client = None # Скидаємо клієнт у None, щоб спробувати ще раз
                        return None
                else:
                    telethon_logger.info("Telethon клієнт вже авторизований.")

            except Exception as e:
                telethon_logger.error(f"Помилка при ініціалізації/підключенні Telethon клієнта: {e}", exc_info=True)
                if _telethon_client:
                    await _telethon_client.disconnect()
                _telethon_client = None
                return None
        else:
            # Перевіряємо, чи клієнт досі підключений
            if not _telethon_client.is_connected():
                telethon_logger.info("Існуючий Telethon клієнт не підключений, намагаємося підключитися.")
                try:
                    await _telethon_client.connect()
                    if not await _telethon_client.is_user_authorized():
                        telethon_logger.warning("Telethon клієнт перепідключено, але не авторизовано. Скидаємо клієнт.")
                        await _telethon_client.disconnect()
                        _telethon_client = None
                        return None # Потрібно буде запустити авторизацію знову
                    else:
                        telethon_logger.info("Існуючий Telethon клієнт успішно перепідключено.")
                except Exception as e:
                    telethon_logger.error(f"Помилка при перепідключенні Telethon клієнта: {e}", exc_info=True)
                    _telethon_client = None
                    return None
            else:
                telethon_logger.info("Telethon клієнт вже ініціалізований та підключений.")

    return _telethon_client

async def disconnect_telethon_client():
    """Відключає Telethon клієнт."""
    global _telethon_client
    async with _telethon_lock:
        if _telethon_client and _telethon_client.is_connected():
            telethon_logger.info("Відключення Telethon клієнта.")
            await _telethon_client.disconnect()
            _telethon_client = None
        elif _telethon_client:
            telethon_logger.info("Telethon клієнт не підключений, скидаємо його.")
            _telethon_client = None
        else:
            telethon_logger.info("Telethon клієнт не ініціалізований.")

# Додайте цю функцію для перевірки статусу
async def is_telethon_client_authorized() -> bool:
    """Перевіряє, чи авторизований Telethon клієнт."""
    global _telethon_client
    async with _telethon_lock:
        if _telethon_client and _telethon_client.is_connected():
            return await _telethon_client.is_user_authorized()
        return False