import logging
import asyncio
from aiogram import Bot, Dispatcher
from handlers.start_handler import router as start_router
from handlers.reply_keyboard_handler import router as reply_keyboard_router
from handlers.menu_handler import set_main_menu  # Імпортуємо функцію налаштування меню
from config import BOT_TOKEN

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Реєстрація обробників
dp.include_router(start_router)
dp.include_router(reply_keyboard_router)

async def main():
    logger.info("Бот запускається...")
    # Викликаємо функцію встановлення головного меню
    await set_main_menu(bot)
    logger.info("Головне меню команд встановлено.")
    logger.info("Реєструємо маршрути...")
    logger.info("Маршрути зареєстровані.")
    logger.info("Запускаємо polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())