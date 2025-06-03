# middlewares/telethon_middleware.py

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject # Додайте TelegramObject для універсальності
from aiogram.dispatcher.flags import get_flag # Якщо ви використовуєте get_flag, переконайтесь, що він імпортований


# ВИПРАВЛЕНО: Правильний імпорт TelethonClientManager
try:
    from telegram_client_module.telethon_client import TelethonClientManager
except ImportError:
    logging.warning("TelethonClientManager not found (ImportError in middleware). Telethon functions may not work.")
    class TelethonClientManager:
        def __init__(self):
            self.clients = {}
        async def initialize(self): pass
        async def shutdown(self): pass
        async def get_client(self, phone_number=None): return None

logger = logging.getLogger(__name__)

class TelethonClientMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        logger.info("TelethonClientMiddleware ініціалізовано (без прямого передавання менеджера).")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any] # === ЗМІНА ТУТ: ПОВЕРТАЄМО data як словник ===
    ) -> Any:
        logger.debug(f"TelethonClientMiddleware: Обробка події {event.__class__.__name__}")

        if get_flag(data, "no_telethon_manager"):
            logger.debug("TelethonClientMiddleware: Пропускаю обробку для event без Telethon менеджера (за флагом).")
            return await handler(event, data) # Передаємо data як словник

        dispatcher_obj = data.get("dispatcher")
        if not dispatcher_obj:
            logger.error("TelethonClientMiddleware: Об'єкт 'dispatcher' не знайдено в data.")
            return await handler(event, data) # Передаємо data як словник

        # КОРЕКЦІЯ КЛЮЧА: 'telethon_manager' (це вже було правильно)
        telethon_manager_instance = dispatcher_obj.workflow_data.get('telethon_manager')

        if telethon_manager_instance:
            data["telethon_manager"] = telethon_manager_instance
            logger.debug("TelethonClientMiddleware: Додано 'telethon_manager' до 'data'.")
        else:
            logger.warning("TelethonClientMiddleware: 'telethon_manager' не знайдено в dispatcher.workflow_data. "
                           "Можливо, TelethonClientManager не був ініціалізований або доданий до dispatcher.workflow_data.")

        # === ЗМІНА ТУТ: ПОВЕРТАЄМО data як словник ===
        return await handler(event, data)