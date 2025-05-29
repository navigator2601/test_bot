# utils/logger.py
import logging

# Налаштування формату повідомлень у логах
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

# Основний логер для всього проєкту
logger = logging.getLogger('bot_logger')
logger.setLevel(logging.INFO) # Всі повідомлення рівня INFO і вище будуть оброблятися

# Обробник для виводу логів у консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG) # В консоль виводимо DEBUG і вище (для більш детальної інформації)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Додаємо обробники до логера, якщо їх ще немає
if not logger.handlers:
    logger.addHandler(console_handler)

# Приклад використання в інших модулях:
# from utils.logger import logger
# logger.info("Це інформаційне повідомлення з іншого модуля.")