# middlewares/dependencies.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update # Додано Update для обробки винятків
import logging

logger = logging.getLogger(__name__)

class DependenciesMiddleware(BaseMiddleware):
    def __init__(self, db_pool: Any, telethon_manager: Any):
        # Зберігаємо об'єкти, які потрібно ін'єктувати
        self.db_pool = db_pool
        self.telethon_manager = telethon_manager
        logger.info("DependenciesMiddleware ініціалізовано.")

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Додаємо об'єкти в словник data, щоб вони були доступні в хендлерах
        data["db_pool"] = self.db_pool
        data["telethon_manager"] = self.telethon_manager
        logger.debug(f"DependenciesMiddleware: db_pool та telethon_manager додано до data для події {type(event).__name__}.")
        return await handler(event, data)

class ExceptionHandlingMiddleware(BaseMiddleware):
    def __init__(self):
        logger.info("ExceptionHandlingMiddleware ініціалізовано.")

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Виникла глобальна помилка: {e}", exc_info=True)
            user_id = None
            chat_id = None

            if isinstance(event, Message):
                user_id = event.from_user.id
                chat_id = event.chat.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                chat_id = event.message.chat.id if event.message else None
            
            error_message_for_user = "Виникла неочікувана помилка. Будь ласка, спробуйте пізніше або зв'яжіться з адміністратором."

            # Тут ви можете додати більш специфічну обробку помилок.
            # Наприклад, для Telethon та asyncpg можна імпортувати їхні винятки.
            import asyncpg
            from telethon.errors import RPCError # Припускаємо, що це основний тип помилки Telethon

            if isinstance(e, asyncpg.exceptions.PostgresError):
                error_message_for_user = "Виникла проблема з базою даних. Ми вже працюємо над її вирішенням!"
            elif isinstance(e, RPCError):
                error_message_for_user = f"Виникла помилка Telegram API: {e}. Спробуйте ще раз."
            else:
                # Для інших неочікуваних помилок
                logger.critical(f"Критична неочікувана помилка: {e}", exc_info=True)
                error_message_for_user = "Сталася критична помилка в системі. Адміністратора повідомлено."
            
            if chat_id:
                try:
                    # Важливо: Event може бути CallbackQuery, і він не має метода .answer().
                    # Ми хочемо надіслати повідомлення в чат.
                    if isinstance(event, CallbackQuery) and event.message:
                        await event.message.answer(error_message_for_user)
                        # Якщо це CallbackQuery, також бажано відповісти на callback, щоб прибрати "годинник"
                        await event.answer("Виникла помилка. Деталі у повідомленні.")
                    elif isinstance(event, Message):
                        await event.answer(error_message_for_user)

                except Exception as send_e:
                    logger.error(f"Не вдалося надіслати повідомлення про помилку користувачеві {user_id}: {send_e}", exc_info=True)
            return