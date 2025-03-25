from telegram.ext import Application
from config import BOT_TOKEN
from handlers.start_handler import start_handler
from handlers.info_handler import info_handler, callback_handler
import logging

logging.basicConfig(level=logging.INFO)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Додаємо обробники
    application.add_handler(start_handler)
    application.add_handler(info_handler)
    application.add_handler(callback_handler)

    logging.info("✅ Бот запущено...")
    application.run_polling()

if __name__ == "__main__":
    main()
