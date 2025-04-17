import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.menu_handler import set_main_menu
from handlers.start_handler import router
from utils.logger import setup_logger
from flask import Flask
import os
import threading

# Налаштування логування
logger = setup_logger("__main__")

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ініціалізація Flask для роботи на Cloud Run
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    """
    Перевірка стану сервісу для Cloud Run.
    """
    return "Bot is running!", 200

def start_web_server():
    """
    Запускає Flask сервер у окремому потоці.
    """
    port = int(os.environ.get("PORT", 8080))  # Cloud Run використовує порт 8080 за замовчуванням
    app.run(host="0.0.0.0", port=port)

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
        # Запуск Flask сервера у окремому потоці
        threading.Thread(target=start_web_server, daemon=True).start()

        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинено.")