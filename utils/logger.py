# utils/logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import datetime # Імпортуємо datetime для мілісекунд
from config import config # Імпортуємо єдиний об'єкт конфігурації

# --- Кастомний клас форматування логів ---
class RefridexFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Отримуємо час з мілісекундами
        dt = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime("%Y-%m-%d %H:%M:%S")
        return f"{s}.{int(record.msecs):03d}"

    # Визначаємо формат для кожного рівня логування
    FORMATS = {
        logging.DEBUG: "[Refridex OS • DEBUG • %(asctime)s] 🐞 Відлагодження: %(name)s • %(message)s",
        logging.INFO: "[Refridex OS • LOGCORE • %(asctime)s] 🔹 Стан: %(name)s • %(message)s",
        logging.WARNING: "[Refridex OS • УВАГА • %(asctime)s] ⚠️ Попередження: %(name)s • %(message)s",
        logging.ERROR: "[Refridex OS • ПОМИЛКА • %(asctime)s] ❌ Помилка: %(name)s • %(message)s",
        logging.CRITICAL: "[Refridex OS • КРИТИЧНО • %(asctime)s] 💥 КРИТИЧНА ПОМИЛКА: %(name)s • %(message)s"
    }

    def format(self, record):
        # Обираємо формат залежно від рівня логування
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO]) # За замовчуванням INFO
        
        # Створюємо тимчасовий форматер з вибраним шаблоном
        formatter = logging.Formatter(log_fmt)
        
        # Встановлюємо наш кастомний formatTime
        formatter.formatTime = self.formatTime
        
        # Форматуємо запис
        return formatter.format(record)
# --- Кінець кастомного класу форматування логів ---


def setup_logging():
    """
    Налаштовує логування для бота, включаючи файлове логування та вивід у консоль.
    Логує всі події, починаючи з рівня DEBUG.
    """
    # Створюємо директорію для логів, якщо її немає.
    os.makedirs(config.logs_dir, exist_ok=True)

    # Головний логер
    main_logger = logging.getLogger()
    # Встановлюємо загальний рівень для всіх обробників (для main_logger)
    main_logger.setLevel(logging.DEBUG) 

    # Якщо вже є обробники, видаляємо їх, щоб уникнути дублювання
    if main_logger.hasHandlers():
        main_logger.handlers.clear()

    # Створюємо екземпляр нашого кастомного форматера
    refridex_formatter = RefridexFormatter()

    # 1. Обробник для виводу в консоль (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # У консоль виводимо від INFO і вище
    console_handler.setFormatter(refridex_formatter) # Використовуємо кастомний форматер
    main_logger.addHandler(console_handler)

    # 2. Обробник для запису логів бота у файл (TimedRotatingFileHandler)
    bot_file_handler = TimedRotatingFileHandler(
        config.bot_log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    bot_file_handler.setLevel(logging.DEBUG) # У файл бота пишемо все від DEBUG
    bot_file_handler.setFormatter(refridex_formatter) # Використовуємо кастомний форматер
    main_logger.addHandler(bot_file_handler)

    # 3. Обробник для запису логів останнього входу Telethon (може бути окремим)
    login_file_handler = TimedRotatingFileHandler(
        config.last_login_log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    login_file_handler.setLevel(logging.INFO) # У файл логу входу пишемо від INFO
    login_file_handler.setFormatter(refridex_formatter) # Використовуємо кастомний форматер
    main_logger.addHandler(login_file_handler)

    # Додаткові налаштування для логування від бібліотек (знижуємо рівень, щоб не було занадто багато шуму)
    logging.getLogger('telethon').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('asyncpg').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

    # Закоментуємо print("Логування налаштовано."), оскільки тепер це буде логуватися
    # інакше ми побачимо стандартний print перед налаштованим логом.
    # print("Логування налаштовано.")
    logging.getLogger(__name__).info("Логування налаштовано.") # Використовуємо логер для повідомлення

# Якщо файл запущено напряму, просто налаштовуємо логування
if __name__ == '__main__':
    setup_logging()
    # Приклад використання логера:
    # Отримуємо логер для цього конкретного файлу
    test_logger = logging.getLogger(__name__) 
    test_logger.debug("Це повідомлення рівня DEBUG")
    test_logger.info("Це повідомлення рівня INFO")
    test_logger.warning("Це попередження (WARNING)")
    test_logger.error("Це помилка (ERROR)")
    test_logger.critical("Це критична помилка (CRITICAL)")
    
    # Використовуємо config.logs_dir, який вже імпортовано
    test_logger.info(f"Логи можна знайти в директорії: {config.logs_dir}")