# handlers/start_handler.py
# Обробник команди запуску
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext # Додано імпорт
from aiogram.client.bot import Bot # Додано імпорт
from keyboards.reply_keyboard import create_paginated_keyboard
from utils.logger import logger
from utils.auth_check import handle_user_on_start
import asyncio

# Ініціалізація маршрутизатора
router = Router(name="Обробник команди запуску")
module_logger = logger.getChild(__name__)

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext, bot: Bot): # ОНОВЛЕНО: додано state та bot
    user = message.from_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    full_name = f"{first_name} {last_name}".strip()
    module_logger.info(f"Користувач {full_name} (@{username}) (ID: {user_id}) виконав команду /start.")

    # ЦІ РЯДКИ Є КЛЮЧОВИМИ
    user_db_data = await handle_user_on_start(user_id, username, first_name, last_name)
    # ПОТРІБНО ПЕРЕВІРИТИ ЗНАЧЕННЯ access_level ОДРАЗУ ПІСЛЯ ЙОГО ОТРИМАННЯ
    access_level = user_db_data.get("access_level", 0) if user_db_data else 0
    
    # ДОДАЙТЕ ЛОГУВАННЯ ТУТ!
    module_logger.debug(f"У start_command: Отриманий access_level з user_db_data: {access_level}")


    welcome_text = (
        f"👋 Привіт, {first_name}! Я бот-помічник з кондиціонерів ❄️.\n\n"
        "Радий бачити вас! Почнімо роботу.\n"
        "Ось головне меню:"
    )

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(2)
    
    # ВИПРАВЛЕНО: Прибрано 'await' перед create_paginated_keyboard
    await message.answer(welcome_text, reply_markup=create_paginated_keyboard(page=1, user_access_level=access_level))
    await state.clear() # Додано очищення стану

def register_handlers(dp):
    dp.include_router(router)