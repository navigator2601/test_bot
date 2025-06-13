# middlewares/exception_middleware.py
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

# Імпортуємо специфічні винятки, які хочемо розпізнавати
import asyncpg
from telethon.errors import RPCError, FloodWaitError, AuthKeyError, SessionPasswordNeededError # Додайте інші важливі для Telethon винятки

logger = logging.getLogger(__name__)

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
            # Спробувати виконати основний обробник
            return await handler(event, data)
        except Exception as e:
            # Обробка винятків
            logger.error(f"Виникла глобальна помилка під час обробки оновлення {event.update_id}: {e}", exc_info=True)
            
            user_id = None
            chat_id = None
            message_to_send = "Виникла неочікувана помилка. Будь ласка, спробуйте пізніше або зв'яжіться з адміністратором."

            if isinstance(event, Message):
                user_id = event.from_user.id
                chat_id = event.chat.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                chat_id = event.message.chat.id if event.message else None
            
            # Специфічна обробка відомих винятків
            if isinstance(e, asyncpg.exceptions.PostgresError):
                message_to_send = "Виникла проблема з базою даних. Ми вже працюємо над її вирішенням!"
            elif isinstance(e, FloodWaitError):
                message_to_send = f"Надто багато запитів! Спробуйте знову через {e.seconds} секунд."
            elif isinstance(e, RPCError):
                message_to_send = f"Виникла помилка Telegram API: {e}. Перевірте дані або спробуйте знову."
            elif isinstance(e, (AuthKeyError, SessionPasswordNeededError)):
                message_to_send = "Помилка авторизації Telethon-клієнта. Можливо, потрібна повторна авторизація."
            # Додайте інші типи винятків, які ви хочете обробляти по-особливому
            else:
                # Для всіх інших невідомих помилок
                logger.critical(f"Критична неперехоплена помилка: {e}", exc_info=True)
                message_to_send = "Сталася критична помилка в системі. Адміністратора вже повідомлено."
            
            # Надіслати повідомлення користувачеві
            if chat_id:
                try:
                    if isinstance(event, CallbackQuery) and event.message:
                        await event.message.answer(message_to_send)
                        await event.answer("Виникла помилка. Деталі у повідомленні.")
                    elif isinstance(event, Message):
                        await event.answer(message_to_send)
                except Exception as send_e:
                    logger.error(f"Не вдалося надіслати повідомлення про помилку користувачеві {user_id}: {send_e}", exc_info=True)
            
            # Повернути None, щоб перервати подальшу обробку цього оновлення основним хендлером
            return