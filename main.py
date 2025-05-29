# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, DATABASE_URL, TELEGRAM_PHONE
from database.db_pool_manager import create_db_pool, get_db_pool, close_db_pool
from telethon_client import TelethonClientManager # <-- Розкоментуй цей рядок

from handlers import start_handler
from handlers import menu_handler
from handlers import echo_handler # Якщо у тебе є handlers/echo_handler.py

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Логування налаштовано.")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def start_telethon_client_task(dispatcher: Dispatcher, db_pool_instance):
    """Окрема функція для запуску Telethon клієнта як завдання."""
    logger.info("Telethon клієнт: Запуск у фоновому режимі.")
    try:
        telethon_manager = TelethonClientManager(db_pool=db_pool_instance)
        dispatcher["telethon_manager"] = telethon_manager

        telethon_client = await telethon_manager.start_client()

        if telethon_client and await telethon_client.is_user_authorized():
            me = await telethon_client.get_me()
            logger.info(f"Telethon клієнт підключений та авторизований як @{me.username or me.first_name}")
        else:
            logger.warning("Telethon клієнт не авторизований або не підключений після запуску. Можливо, потрібна ручна авторизація.")

    except Exception as e:
        logger.critical(f"Критична помилка при ініціалізації Telethon клієнта: {e}", exc_info=True)
        # Не виходимо з програми, щоб не зупиняти Aiogram бота
        # Але цей блок все одно відобразить критичну помилку
        pass # Продовжуємо виконання, бот Aiogram може працювати і без Telethon


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logger.info("Бот запускається: Початок on_startup.")

    try:
        await create_db_pool()
        db_pool_instance = await get_db_pool()
        dispatcher["db_pool"] = db_pool_instance
        logger.info("Підключення до бази даних встановлено.")
    except Exception as e:
        logger.critical(f"Критична помилка при підключенні до бази даних: {e}", exc_info=True)
        exit(1)

    logger.info("on_startup: База даних ініціалізована.")

    # Запускаємо Telethon клієнт як фонове завдання
    asyncio.create_task(start_telethon_client_task(dispatcher, db_pool_instance))

    logger.info("on_startup: Завершення on_startup.")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    logger.info("Бот вимикається: Початок on_shutdown.")

    telethon_manager = dispatcher.get("telethon_manager")
    if telethon_manager:
        await telethon_manager.disconnect_client()
        logger.info("on_shutdown: Telethon клієнт відключено.")

    await close_db_pool()
    logger.info("Підключення до бази даних закрито.")

    logger.info("Бот зупинено.")


async def main() -> None:
    logger.info("Main: Реєстрація хендлерів запуску/зупинки.")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Main: Включення роутерів.")
    dp.include_router(start_handler.router)
    dp.include_router(menu_handler.router)
    # Якщо у тебе є handlers/echo_handler.py, розкоментуй наступний рядок:
    dp.include_router(echo_handler.router) # Якщо є такий файл

    logger.info("Main: Перед запуском dp.start_polling.")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    logger.info("Main: dp.start_polling завершився (це не повинно відбуватися, якщо бот працює).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено вручну (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Критична помилка під час запуску бота: {e}", exc_info=True)