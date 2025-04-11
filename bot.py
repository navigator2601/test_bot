import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import register_handlers
from database import init_db

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Створюємо екземпляр бота
bot = Bot(token=BOT_TOKEN)  # Не передаємо parse_mode сюди
dp = Dispatcher()

async def set_bot_commands():
    """Функція для встановлення команд бота."""
    commands = [
        BotCommand(command="/start", description="Запустити бота"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Ініціалізація бази даних
    await init_db()

    # Встановлюємо команди бота
    await set_bot_commands()

    # Реєстрація обробників
    register_handlers(dp)

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info("Запуск бота...")
    asyncio.run(main())