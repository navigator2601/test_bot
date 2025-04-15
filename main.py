import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.start_handler import register_start_handler  # Імпортуємо обробник для команди /start
from handlers.text_handler import register_text_handler
from handlers.menu_handler import set_main_menu, register_menu_handlers  # Імпортуємо обробники меню
from utils.logger import get_logger

# Отримуємо логер
logger = get_logger(__name__)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)

# Ініціалізація диспетчера
dp = Dispatcher()

# Головна функція запуску бота
async def main():
    logger.info("Бот запускається...")

    # Встановлення головного меню
    logger.info("Встановлюємо головне меню команд...")
    await set_main_menu(bot)

    # Реєстрація обробників
    register_start_handler(dp)
    register_text_handler(dp)
    register_menu_handlers(dp)

    logger.info("Обробники команд зареєстровані.")

    # Запуск опитування
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Виникла помилка під час запуску бота: {e}")
    finally:
        logger.info("Бот завершив роботу.")

if __name__ == "__main__":
    asyncio.run(main())