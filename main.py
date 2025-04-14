import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.start_handler import register_start_handler
from handlers.text_handler import register_text_handler

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)

# Ініціалізація диспетчера
dp = Dispatcher()

# Головна функція запуску бота
async def main():
    logging.info("Бот запускається...")

    # Реєстрація обробників
    register_start_handler(dp)
    register_text_handler(dp)

    # Запуск опитування
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())