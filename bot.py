import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers.start import register_handlers_start
from handlers.user import register_handlers_user
from middlewares import LoggingMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.update.middleware(LoggingMiddleware())

register_handlers_start(dp)
register_handlers_user(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())