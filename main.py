# main.py

import asyncio
import logging
from typing import Any

# Імпорти Aiogram
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Імпорти для вашої конфігурації та логування
from config import config
from utils.logger import setup_logging

# Імпорти для БД та Мідлвари
from database.db_pool_manager import create_db_pool, close_db_pool, init_db_tables, get_db_pool
from middlewares.db_middleware import DbSessionMiddleware

# --- НОВІ ІМПОРТИ для Telethon ---
from telegram_client_module.telethon_client import TelethonClientManager
from middlewares.telethon_middleware import TelethonClientMiddleware
# -----------------------------------

# Імпорти для роутерів
from handlers.start_handler import router as start_router
from handlers.menu_handler import router as menu_router

# НАЙПЕРШИЙ ВИКЛИК налаштування логів
setup_logging()
logger = logging.getLogger(__name__)

# Глобальний екземпляр TelethonManager
telethon_manager: TelethonClientManager = None


async def on_bot_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    """
    Функція, що виконується при запуску бота.
    Ініціалізує пул підключень до БД, таблиці та Telethon-клієнти.
    """
    logger.info("Початок запуску бота. Зареєстровані startup-хуки виконуються.")

    global telethon_manager # Оголошуємо, що будемо змінювати глобальну змінну

    logger.info("Спроба створити пул підключень до бази даних.")
    try:
        await create_db_pool()
        db_pool_instance = await get_db_pool()
        dispatcher.workflow_data['db_pool'] = db_pool_instance
        logger.info("Пул підключень до бази даних створено успішно.")
    except Exception as e:
        logger.critical(f"Критична помилка підключення до бази даних: {e}", exc_info=True)
        await bot.session.close()
        exit(1)

    logger.info("Ініціалізація таблиць бази даних.")
    try:
        await init_db_tables()
        logger.info("Таблиці бази даних ініціалізовано.")
    except Exception as e:
        logger.error(f"Помилка ініціалізації таблиць БД: {e}", exc_info=True)

    # --- ЛОГІКА TELETHON: ІНІЦІАЛІЗАЦІЯ та ЗАПУСК ---
    logger.info("Ініціалізація TelethonClientManager.")
    # ЗМІНА ТУТ: Створюємо без аргументів
    telethon_manager = TelethonClientManager()
    # І ТУТ: Викликаємо метод initialize()
    await telethon_manager.initialize()

    # Зберігаємо менеджер у workflow_data для доступу через мідлвари та хендлери
    dispatcher.workflow_data['telethon_manager'] = telethon_manager
    logger.info("TelethonClientManager ініціалізовано.")

    # Логіка запуску клієнтів вже всередині telethon_manager.initialize(),
    # тому тут вже не потрібен окремий виклик telethon_manager.start_all_clients()
    # Просто перевіряємо, чи були клієнти запущені.

    if config.telethon_client_enabled:
        # Лог буде повідомляти, що клієнти вже запущені всередині initialize()
        logger.info("Telethon клієнти налаштовано та, якщо потрібно, запущені (через initialize()).")
    else:
        logger.warning("Telethon клієнти вимкнено через конфігурацію. Пропускаю їх запуск.")
    # --------------------------------------------------

    logger.info("Завершення on_startup.")

async def on_bot_shutdown(bot: Bot, dispatcher: Dispatcher) -> None:
    """
    Функція, що виконується при завершенні роботи бота.
    Закриває пул підключень до БД та відключає Telethon-клієнти.
    """
    logger.info("Початок завершення роботи бота. Зареєстровані shutdown-хуки виконуються.")

    global telethon_manager # Оголошуємо, що будемо використовувати глобальну змінну

    # --- ЛОГІКА TELETHON: ЗУПИНКА КЛІЄНТІВ ---
    if telethon_manager and config.telethon_client_enabled:
        logger.info("Спроба відключити Telethon клієнтів.")
        try:
            # Викликаємо метод shutdown() замість stop_all_clients()
            await telethon_manager.shutdown()
            logger.info("Telethon клієнти відключено.")
        except Exception as e:
            logger.error(f"Помилка відключення Telethon клієнтів: {e}", exc_info=True)
    # ------------------------------------------

    logger.info("Спроба закрити пул підключень до бази даних.")
    try:
        await close_db_pool()
        logger.info("Пул підключень до бази даних закрито.")
    except Exception as e:
        logger.error(f"Помилка закриття пулу БД: {e}", exc_info=True)

    logger.info("Закриття сесії бота.")
    await bot.session.close()
    logger.info("Сесію бота закрито.")

async def main():
    logger.info("Початок виконання головної асинхронної функції 'main'.")

    if not config.bot_token:
        logger.critical("BOT_TOKEN не встановлено у файлі конфігурації. Будь ласка, перевірте .env та config.py.")
        return

    default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)

    logger.info("Ініціалізація об'єкта Bot.")
    bot = Bot(token=config.bot_token, default=default_props)

    storage = MemoryStorage()

    logger.info("Ініціалізація об'єкта Dispatcher.")
    dp = Dispatcher(storage=storage)

    logger.info("Реєстрація DbSessionMiddleware.")
    dp.update.outer_middleware.register(DbSessionMiddleware())
    logger.info("DbSessionMiddleware зареєстровано глобально.")

    # --- РЕЄСТРАЦІЯ TELETHON МІДЛВАРИ ---
    if config.telethon_client_enabled:
        logger.info("Реєстрація TelethonClientMiddleware.")
        dp.update.outer_middleware.register(TelethonClientMiddleware())
        logger.info("TelethonClientMiddleware зареєстровано глобально.")
    else:
        logger.warning("TelethonClientMiddleware не реєструється (вимкнено через конфігурацію).")
    # ------------------------------------

    # Реєстрація роутерів
    logger.info("Реєстрація роутера 'start_handler'.")
    dp.include_router(start_router)
    if menu_router:
        logger.info("Реєстрація роутера 'menu_handler'.")
        dp.include_router(menu_router)

    # Реєстрація функцій запуску/зупинки
    dp.startup.register(on_bot_startup)
    dp.shutdown.register(on_bot_shutdown)

    logger.info("Перед викликом dp.start_polling. Бот чекає на оновлення...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критична помилка під час polling: {e}", exc_info=True)

    logger.info("dp.start_polling завершив роботу.")


if __name__ == "__main__":
    logger.info("Ядро ініціалізовано: активація блоку `if __name__ == '__main__'` розпочата...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено вручну (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Критична помилка в основному циклі: {e}", exc_info=True)
    logger.info("Система: процес завершено. Вихід з потоку.")