# main.py
import asyncio
import os
from aiogram import Bot, Dispatcher, types 
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from utils.logger import logger
# Важливо: імпортуємо функції для роботи з базою даних, включаючи create_db_pool та close_db_pool
from database.users_db import create_db_pool, close_db_pool, get_user_data 

from handlers import start_handler
from handlers import admin_handler # ІМПОРТУЄМО АДМІН-ОБРОБНИК
from handlers.reply_keyboard_handler import router as reply_keyboard_router
from handlers.menu_handler import set_main_menu
# <<<< ІМПОРТУЄМО ФУНКЦІЇ TELETHON КЛІЄНТА, ВКЛЮЧАЮЧИ get_telethon_client_instance
from telethon_client import get_telethon_client_instance, disconnect_telethon_client 

load_dotenv() # Завантажуємо змінні оточення з .env файлу

main_logger = logger.getChild(__name__) # Логер для головного файлу

async def main():
    main_logger.info("==================== Запуск бота ====================")

    # Ініціалізуємо пул з'єднань з базою даних
    db_initialized = await create_db_pool() 
    if not db_initialized:
        main_logger.critical("Не вдалося ініціалізувати пул з'єднань з базою даних. Завершення роботи.")
        return

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        main_logger.critical("BOT_TOKEN не встановлено в .env файлі!")
        raise ValueError("BOT_TOKEN environment variable is not set")

    # <<<< ДУЖЕ ВАЖЛИВО: ІНІЦІАЛІЗУЄМО TELETHON КЛІЄНТ НА СТАРТІ БОТА
    main_logger.info("Спроба ініціалізації Telethon клієнта...")
    try:
        # Цей виклик спробує завантажити існуючу сесію або запустити процес авторизації
        # якщо клієнт ще не авторизований.
        await get_telethon_client_instance() 
        main_logger.info("Telethon клієнт ініціалізовано або завантажено сесію.")
    except Exception as e:
        main_logger.error(f"Помилка при початковій ініціалізації Telethon клієнта: {e}", exc_info=True)
        # На цьому етапі ви можете вирішити, чи потрібно зупинити бота, якщо Telethon не може запуститися.
        # Наприклад, якщо функціонал бота сильно залежить від Telethon, ви можете додати:
        # return 
    
    dp = Dispatcher() # Створюємо об'єкт диспетчера Aiogram
    # Створюємо об'єкт бота, вказуючи токен та режим парсингу HTML для повідомлень
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) 

    main_logger.info("Реєстрація обробників...")
    # ВКЛЮЧАЄМО ВСІ РОУТЕРИ (обробники) ДО ДИСПЕТЧЕРА
    # Порядок включення роутерів може бути важливим для обробки команд
    dp.include_routers(
        start_handler.router,
        reply_keyboard_router,
        admin_handler.router, # ЦЕЙ РЯДОК ДУЖЕ ВАЖЛИВИЙ ДЛЯ АДМІН-ФУНКЦІОНАЛУ, він реєструє всі обробники з admin_handler.py
        # Додайте інші маршрутизатори, якщо вони у вас є (наприклад, file_handler.router, text_handler.router, etc.)
    )
    main_logger.info("Обробники зареєстровано.")

    main_logger.info("Встановлення команд головного меню...")
    await set_main_menu(bot) # Встановлюємо команди меню бота, які відображаються у Telegram
    main_logger.info("Головне меню команд встановлено.")

    main_logger.info("Бот запущено в режимі Long Polling.")
    # Запускаємо бота в режимі Long Polling, який постійно слухає нові оновлення
    try:
        await dp.start_polling(bot) 
    except Exception as e:
        main_logger.critical(f"Непередбачена помилка в головному циклі: {e}", exc_info=True)
    finally:
        main_logger.info("Завершення роботи бота...")
        # Закриваємо пул з'єднань з БД при завершенні роботи бота, щоб уникнути витоків ресурсів
        await close_db_pool() 
        # <<<< ДУЖЕ ВАЖЛИВО: Викликаємо disconnect_telethon_client() тут
        await disconnect_telethon_client() 
        await bot.session.close() # Закриваємо сесію aiogram бота
        main_logger.info("==================== Бот зупинено ====================")

if __name__ == "__main__":
    try:
        asyncio.run(main()) # Запускаємо асинхронну функцію main()
    except KeyboardInterrupt:
        main_logger.info("Бот зупинено вручну (KeyboardInterrupt).")
    except Exception as e:
        main_logger.critical(f"Непередбачена помилка при запуску бота: {e}", exc_info=True)
    # Зверніть увагу: `finally` у `main()` функції виконається,
    # навіть якщо виникне KeyboardInterrupt у `asyncio.run`.