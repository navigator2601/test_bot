# handlers/start_handler.py
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import logging
from database import users_db # Імпортуємо модуль для роботи з користувачами в БД
# from datetime import datetime, timezone # Ці імпорти вже є в users_db, тому не потрібні тут безпосередньо

import asyncpg # Додаємо імпорт asyncpg для тайпінгу (типування) db_pool

logger = logging.getLogger(__name__)

router = Router()

# Додаємо db_pool: asyncpg.Pool як аргумент функції
@router.message(CommandStart())
async def command_start_handler(message: types.Message, db_pool: asyncpg.Pool) -> None:
    """
    Обробник команди /start.
    Перевіряє користувача в БД, оновлює його або додає нового.
    Відправляє привітальне повідомлення.
    """
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name # Отримуємо лише ім'я
    user_username = message.from_user.username # Може бути None
    user_last_name = message.from_user.last_name # Може бути None

    logger.info(f"Користувач {user_first_name} (ID: {user_id}) виконав команду /start.")

    # db_pool тепер передається як аргумент, тому перевірка "if not db_pool" не потрібна
    # Але це гарна практика для інших випадків, якщо не впевнений, що він завжди буде
    # Наразі, вона стала зайвою, бо aiogram або передасть пул, або викличе помилку до обробника.

    # Перевіряємо, чи існує користувач у базі даних
    user = await users_db.get_user(db_pool, user_id)

    if user:
        # Якщо користувач існує, оновлюємо його останню активність
        await users_db.update_user_activity(db_pool, user_id)
        logger.info(f"Оновлено last_activity для існуючого користувача {user_id}.")
    else:
        # Якщо користувача немає, додаємо його
        await users_db.add_user(db_pool, user_id, user_username, user_first_name, user_last_name)
        logger.info(f"Додано нового користувача {user_id} до БД.")

    # Текст привітання з використанням HTML-форматування
    welcome_message = f"""
<b>"Вітаю, майстре охолодження, {user_first_name}.</b>
Рефрідекс активовано.
Підключення до бази Конди-Ленду успішне.
Починаю синхронізацію моделей, трас і фреонів.
Твій шлях крізь жар і мідь — під моїм наглядом.
Нехай монтаж буде рівним, а фреон — у нормі."
"""
    await message.answer(welcome_message, parse_mode=ParseMode.HTML)