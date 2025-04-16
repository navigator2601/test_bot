import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file="logs/bot.log", level=logging.INFO):
    """
    Налаштування логування із заданим форматом, що записує логи у файл з ротацією.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ротація логів: 5MB і 3 резервні копії
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    # Додавання хендлера для запису у файл
    logger.addHandler(handler)

    # Вивід логів у консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger