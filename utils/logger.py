import logging
from logging.handlers import RotatingFileHandler
import os

# Створюємо директорію для логів, якщо її немає
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Шлях до файлу логування
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# Формат логів
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,  # Базовий рівень логування
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Логування у консоль
        RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)  # Логування у файл
    ]
)

# Отримуємо логер
def get_logger(name: str) -> logging.Logger:
    """
    Повертає логер із заданим ім'ям.

    :param name: Ім'я логера
    :return: Логер
    """
    return logging.getLogger(name)