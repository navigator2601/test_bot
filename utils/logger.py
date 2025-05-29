# utils/logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from config import LOGS_DIR, BOT_LOG_FILE, LAST_LOGIN_LOG_FILE

def setup_logging():
    """
    Налаштовує логування для бота, включаючи файлове логування та вивід у консоль.
    Логує всі події, починаючи з рівня DEBUG.
    """
    # Створюємо директорію для логів, якщо її немає (це вже робиться в config.py, але можна продублювати для безпеки)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Головний логер
    main_logger = logging.getLogger()
    main_logger.setLevel(logging.DEBUG) # Логуємо все, починаючи з DEBUG

    # Якщо вже є обробники, видаляємо їх, щоб уникнути дублювання
    if main_logger.hasHandlers():
        main_logger.handlers.clear()

    # Форматтер для логів
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 1. Обробник для виводу в консоль (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # У консоль виводимо від INFO і вище
    console_handler.setFormatter(formatter)
    main_logger.addHandler(console_handler)

    # 2. Обробник для запису логів бота у файл (TimedRotatingFileHandler)
    # Файл буде змінюватися щодня опівночі, зберігаючи до 7 попередніх файлів.
    bot_file_handler = TimedRotatingFileHandler(
        BOT_LOG_FILE,
        when="midnight", # Міняти файл щодня опівночі
        interval=1,
        backupCount=7,   # Зберігати 7 попередніх файлів
        encoding='utf-8'
    )
    bot_file_handler.setLevel(logging.DEBUG) # У файл бота пишемо все від DEBUG
    bot_file_handler.setFormatter(formatter)
    main_logger.addHandler(bot_file_handler)

    # 3. Обробник для запису логів останнього входу Telethon (може бути окремим)
    # Це може бути корисно для відстеження авторизації Telethon.
    login_file_handler = TimedRotatingFileHandler(
        LAST_LOGIN_LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    login_file_handler.setLevel(logging.INFO) # У файл логу входу пишемо від INFO
    login_file_handler.setFormatter(formatter)
    # Можемо створити окремий логер для Telethon або використовувати основний з фільтром
    # Для простоти поки додамо до основного, але в майбутньому можна розділити.
    main_logger.addHandler(login_file_handler)

    # Додаткові налаштування для логування від бібліотек (наприклад, SQLAlchemy, Telethon)
    # Це важливо, щоб приглушити їхній власний шум або, навпаки, ввімкнути детальний лог.

    # Приглушуємо логування від Telethon, якщо воно занадто багатослівне,
    # або встановлюємо DEBUG, якщо хочемо бачити все.
    logging.getLogger('telethon').setLevel(logging.WARNING)
    # logging.getLogger('telethon').setLevel(logging.DEBUG) # Якщо потрібен детальний лог Telethon

    # Приглушуємо логування від aiogram, якщо воно занадто багатослівне.
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    # logging.getLogger('aiogram').setLevel(logging.DEBUG) # Якщо потрібен детальний лог aiogram

    # Приглушуємо логування від asyncpg
    logging.getLogger('asyncpg').setLevel(logging.WARNING)

    # Приглушуємо логування від SQLAlchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)


    print("Логування налаштовано.")

# Якщо файл запущено напряму, просто налаштовуємо логування
if __name__ == '__main__':
    setup_logging()
    # Приклад використання логера:
    logger = logging.getLogger(__name__)
    logger.debug("Це повідомлення рівня DEBUG")
    logger.info("Це повідомлення рівня INFO")
    logger.warning("Це попередження (WARNING)")
    logger.error("Це помилка (ERROR)")
    logger.critical("Це критична помилка (CRITICAL)")
    print(f"Логи можна знайти в директорії: {LOGS_DIR}")