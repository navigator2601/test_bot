# handlers/start_handler.py

from aiogram import Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import logging
import asyncpg
from typing import Any
from aiogram.fsm.context import FSMContext
from handlers.menu_handler import show_main_menu_handler, MenuStates # <-- ОНОВЛЕНО
from database import users_db

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def command_start_handler(
    message: types.Message,
    bot: Bot,
    db_pool: asyncpg.Pool,
    telethon_manager: Any,
    state: FSMContext # <-- ДОДАНО FSMContext
) -> None:
    """
    Обробник команди /start.
    Перевіряє користувача в БД, оновлює його або додає нового.
    Відправляє привітальне повідомлення та показує головне меню.
    """
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_username = message.from_user.username
    user_last_name = message.from_user.last_name

    logger.info(f"Користувач {user_first_name} (ID: {user_id}) виконав команду /start.")

    if not db_pool:
        logger.error("db_pool не знайдено в аргументах обробника start_handler!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    try:
        user = await users_db.get_user(db_pool, user_id)

        if user:
            await users_db.update_user_activity(db_pool, user_id)
            logger.info(f"Оновлено last_activity для існуючого користувача {user_id}.")
        else:
            await users_db.add_user(db_pool, user_id, user_username, user_first_name, user_last_name)
            logger.info(f"Додано нового користувача {user_id} до БД.")

        welcome_message = f"""
<b>"Вітаю, майстре охолодження, {user_first_name}.</b>
Рефрідекс активовано.
Підключення до бази Конди-Ленду успішне.
Починаю синхронізацію моделей, трас і фреонів.
Твій шлях крізь жар і мідь — під моїм наглядом.
Нехай монтаж буде рівним, а фреон — у нормі."
"""
        await message.answer(welcome_message, parse_mode=ParseMode.HTML)
        logger.info(f"Відправлено привітальне повідомлення користувачу {user_id}.")

        # Встановлюємо початковий стан FSM та номер сторінки
        await state.set_state(MenuStates.main_menu)
        await state.update_data(menu_page=0)

        # ОНОВЛЕНО: Викликаємо show_main_menu_handler і передаємо 'state'
        await show_main_menu_handler(message, bot, db_pool, state)
        logger.info(f"Відображено головне меню для користувача {user_id}.")

    except Exception as e:
        logger.error(f"Помилка обробки команди /start для користувача {user_id}: {e}", exc_info=True)
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте ще раз пізніше.")