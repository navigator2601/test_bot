import logging
import os
from logging.handlers import RotatingFileHandler

# Шлях до лог-файлу
LOG_FILE = "logs/bot.log"

# Перевірка існування папки logs, якщо немає — створюємо
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Створюємо обробник для ротації файлів логів (максимум 5 файлів по 1 МБ)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Налаштування логера
logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Логування у консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)