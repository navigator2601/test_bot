import logging
from aiogram import Router, types
from aiogram.filters import Command

# Ініціалізація роутера
router = Router()
logger = logging.getLogger(__name__)

# Обробник команди /help
@router.message(Command(commands=["help"]))
async def help_command_handler(message: types.Message):
    logger.info(f"Користувач {message.from_user.id} виконав команду /help")
    
    help_text = (
        "🛠 <b>Доступні команди:</b>\n\n"
        "/start - Почати роботу з ботом\n"
        "/help - Список доступних функцій\n"
        "/info - Інформація про бота\n"
        "\n"
        "Для швидкого пошуку введіть будь-яке запитання."
    )
    await message.answer(help_text, parse_mode="HTML")

# Функція реєстрації роутера
def register_help_handler(dp):
    dp.include_router(router)