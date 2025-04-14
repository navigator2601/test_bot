import logging
from aiogram import Router, types
from aiogram.filters import Command

# Ініціалізація роутера
router = Router()
logger = logging.getLogger(__name__)

# Обробник команди /info
@router.message(Command(commands=["info"]))
async def info_command_handler(message: types.Message):
    logger.info(f"Користувач {message.from_user.id} виконав команду /info")
    
    info_text = (
        "ℹ️ <b>Інформація про бота:</b>\n\n"
        "Цей бот створений для допомоги у швидкому пошуку інформації. "
        "Використовуйте меню або команди для взаємодії з ботом. Якщо у вас є питання, "
        "введіть його в поле повідомлення, і бот допоможе вам знайти відповідь.\n\n"
        "<b>Основні можливості:</b>\n"
        "🔹 Пошук інформації\n"
        "🔹 Використання бази даних\n"
        "🔹 Інтерактивна взаємодія\n\n"
        "Для початку роботи скористайтеся командою /start або натисніть кнопку в меню.\n"
        "Приємного користування! 😊"
    )
    await message.answer(info_text, parse_mode="HTML")

# Функція реєстрації роутера
def register_info_handler(dp):
    dp.include_router(router)