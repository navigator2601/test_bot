# main.py
# Головний файл запуску бота
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

async def set_bot_description():
    """
    Встановлює опис бота, який відображається при першому відкритті.
    """
    description = (
        "👋 Привіт! Я бот-помічник з кондиціонерів ❄️.\n\n"
        "Мій функціонал включає:\n"
        "📚 Каталог кондиціонерів із детальними характеристиками.\n"
        "📖 Корисні довідники та відповіді на часті запитання.\n"
        "🕵️ Інтелектуальний пошук інформації.\n"
        "⚠️ Розшифровка кодів помилок для діагностики.\n"
        "🛠️ Інструкції з монтажу та технічна інформація.\n"
        "📐 Додаткові калькулятори та інструменти.\n\n"
        "Натисніть /start, щоб почати роботу. 😊"
    )
    await bot.set_my_description(description)
    logger.info("Опис бота успішно оновлено.")

async def main():
    logger.info("Бот запускається...")
    # Встановлюємо опис бота
    await set_bot_description()
    # Викликаємо функцію встановлення головного меню
    await set_main_menu(bot)
    logger.info("Головне меню команд встановлено.")
    logger.info("Реєструємо маршрути...")
    logger.info("Маршрути зареєстровані.")
    logger.info("Запускаємо polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())