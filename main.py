import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.menu_handler import set_main_menu
from handlers.start_handler import router
from utils.logger import setup_logger

# Налаштування логування
logger = setup_logger("__main__")

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    logger.info("Бот запускається...")

    # Встановлення головного меню команд
    logger.info("Встановлюємо головне меню команд...")
    await set_main_menu(bot)

    # Реєстрація обробників
    logger.info("Реєструємо обробники...")
    dp.include_router(router)
    logger.info("Обробники команд зареєстровані.")

    # Запуск polling
    logger.info("Запускаємо polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинено.")