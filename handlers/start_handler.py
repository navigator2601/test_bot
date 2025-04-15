from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime
import asyncio
from keyboards.reply_keyboard import create_main_menu_keyboard  # Імпорт головного меню
from utils.logger import get_logger  # Підключаємо модуль логування

# Ініціалізація логера
logger = get_logger(__name__)

# Ініціалізація роутера
router = Router()

# Функція визначення привітання відповідно до часу доби
def get_time_based_greeting() -> str:
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 23:
        return "Доброго вечора"
    else:
        return "Доброї ночі"

# Обробник команди /start
@router.message(Command(commands=["start"]))
async def start_command_handler(message: types.Message):
    # Отримуємо дані користувача
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Невідоме ім'я"
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or "Без ніка"

    # Формуємо опис користувача для логування
    user_info = f"{first_name} {last_name} (@{username})" if username != "Без ніка" else f"{first_name} {last_name}".strip()

    # Логування події
    logger.info(f"Користувач {user_info} (ID: {user_id}) виконав команду /start.")

    # Формуємо привітання
    greeting = get_time_based_greeting()

    # Показуємо індикатор набору повідомлення
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)

    # Відправляємо привітання
    await message.answer(
        f"{greeting}, {first_name}!"
    )

    # Показуємо індикатор набору повідомлення перед другим повідомленням
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)

    # Відправляємо основне повідомлення
    await message.answer(
        "Для супроводу у пошуку клікніть потрібну кнопку нижче 👇\n"
        "Для швидкого пошуку просто введіть будь-яку інформацію.",
        reply_markup=create_main_menu_keyboard()
    )

# Функція реєстрації роутера
def register_start_handler(dp):
    dp.include_router(router)