import logging
from aiogram import Router, types
from aiogram.filters import Command
from keyboards.reply_keyboard import get_reply_keyboard
from datetime import datetime

# Ініціалізація роутера
router = Router()
logger = logging.getLogger(__name__)

@router.message(Command(commands=["start"]))
async def start_command_handler(message: types.Message):
    user_name = message.from_user.first_name
    greeting = get_greeting()

    # Логування дії користувача
    logger.info(f"Користувач {message.from_user.id} ({user_name}) виконав команду /start")

    # Відправляємо клавіатуру разом із повідомленням
    await message.answer(
        f"{greeting}, {user_name}!\n"
        "Оберіть потрібний розділ нижче 👇",
        reply_markup=get_reply_keyboard()
    )

# Функція визначення привітання відповідно до часу доби
def get_greeting() -> str:
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 23:
        return "Доброго вечора"
    else:
        return "Доброї ночі"

# Функція реєстрації роутера
def register_start_handler(dp):
    dp.include_router(router)