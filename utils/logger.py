# utils/logger.py
import logging
import os

# Створення директорії logs, якщо вона не існує
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Налаштування базового логера
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Встановлюємо мінімальний рівень логування на DEBUG

# Форматер для логів
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Обробник для запису логів у файл
file_handler = logging.FileHandler(os.path.join(LOGS_DIR, 'bot.log'), encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Обробник для виведення логів у консоль (за бажанням)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Додатковий логер для конкретних модулів (за потреби)
def get_logger(name):
    return logging.getLogger(name)