import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from handlers.user import register_handlers  # Виправлений імпорт

# Завантаження змінних з файлу .env
load_dotenv()

# Зчитування токена бота з .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Перевірка наявності токена
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не задано TELEGRAM_BOT_TOKEN у файлі .env")

# Ініціалізація бота та диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Реєстрація обробників команд
register_handlers(dp)

# Основна функція для запуску бота
async def main():
    try:
        print("Бот запущено...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())