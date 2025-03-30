import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers.user import register_handlers_user

logging.basicConfig(level=logging.INFO)

# Перевірка токену
if not API_TOKEN:
    raise ValueError("No API token provided. Please check your .env file.")

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Реєстрація хендлерів
register_handlers_user(dp)

# Реєстрація стартового хендлера
@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    await message.answer("Hello! I am your bot.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())