from aiogram import Router, types
from aiogram.filters import Command
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command(commands=["settings"]))
async def settings_command_handler(message: types.Message):
    logger.info(f"Користувач {message.from_user.id} виконав команду /settings")
    await message.answer("🛠 Налаштування бота:\n1. Параметр 1\n2. Параметр 2\n\n(Функція в розробці)")