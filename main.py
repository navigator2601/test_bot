import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers.start_handler import register_start_handler
from handlers.help_handler import register_help_handler
from handlers.info_handler import register_info_handler
from handlers.text_handler import register_text_handler

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)

# Ініціалізація диспетчера
dp = Dispatcher()

# Встановлення меню команд
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Почати роботу з ботом"),
        BotCommand(command="help", description="Список доступних функцій"),
        BotCommand(command="info", description="Інформація про бота"),
    ]
    await bot.set_my_commands(commands)
    logging.info("Меню команд успішно встановлено!")

# Головна функція запуску бота
async def main():
    logging.info("Бот запускається...")

    # Встановлення меню команд
    await set_bot_commands()

    # Реєстрація обробників
    register_start_handler(dp)
    register_help_handler(dp)
    register_info_handler(dp)
    register_text_handler(dp)

    # Запуск опитування
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())