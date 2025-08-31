# utils/set_bot_commands.py
from aiogram import Bot, types
import logging

logger = logging.getLogger(__name__)

async def set_default_commands(bot: Bot):
    """
    Встановлює список команд для бота, які відображаються у меню Telegram.
    """
    commands = [
        types.BotCommand(command="start", description="Запустити бота"),
        types.BotCommand(command="help", description="Допомога по використанню бота"),
        types.BotCommand(command="info", description="Отримати інформацію про бота"),
        types.BotCommand(command="find", description="Пошук інформації"),
        types.BotCommand(command="test", description="Кнопка для тесту чи правильний бот "),
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Меню команд успішно встановлено.")
    except Exception as e:
        logger.error(f"Помилка при встановленні меню команд: {e}", exc_info=True)