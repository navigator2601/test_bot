import asyncio
from aiogram import Bot, Dispatcher
from handlers import start
from database import create_pool, create_tables
from config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Підключаємо базу
    pool = await create_pool()
    await create_tables(pool)

    # Реєструємо обробники
    dp.include_router(start.router)

    # Запускаємо бота
    await dp.start_polling(bot, pool=pool)

if __name__ == "__main__":
    asyncio.run(main())
