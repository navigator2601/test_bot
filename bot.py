import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import API_TOKEN
from middlewares import LoggingMiddleware
from handlers.start import register_handlers_start
from handlers.user import register_handlers_user

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Ініціалізація роутера
router = dp.router

# Реєстрація middleware
dp.update.middleware.register(LoggingMiddleware())

# Реєстрація хендлерів
register_handlers_start(router)
register_handlers_user(router)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запуск бота"),
    ]
    await bot.set_my_commands(commands)

if __name__ == '__main__':
    dp.startup.register(set_commands)
    dp.run_polling(bot)