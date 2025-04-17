# Додано стартове меню команд
from aiogram import Bot
from aiogram.types import BotCommand  # Імпорт BotCommand
from utils.logger import setup_logger

# Налаштування логування
logger = setup_logger("handlers.menu_handler")

async def set_main_menu(bot: Bot):
    """
    Функція для встановлення головного меню команд.
    """
    logger.info("Встановлюємо головне меню команд...")

    # Налаштування команд
    commands = [
        ("start", "Почати роботу з ботом"),
        ("help", "Список доступних команд"),
        ("info", "Інформація про бота")
    ]

    # Встановлення команд у меню бота
    try:
        await bot.set_my_commands([
            BotCommand(command, description) for command, description in commands
        ])
        logger.info("Головне меню команд успішно встановлено.")
    except Exception as e:
        logger.error(f"Помилка при встановленні головного меню команд: {e}")