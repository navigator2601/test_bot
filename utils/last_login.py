# utils/last_login.py
# Логування останнього входу користувачів
import logging
import os
from logging.handlers import RotatingFileHandler

# Шлях до лог-файлу для входів користувачів
LOG_FILE = "logs/last_login.log"

# Перевірка існування папки logs, якщо немає — створюємо
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Створюємо обробник для логів у файл
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=500_000, backupCount=3, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))

# Створюємо обробник для виводу в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))

# Налаштування логера
login_logger = logging.getLogger("last_login_logger")
login_logger.setLevel(logging.INFO)
login_logger.addHandler(file_handler)
login_logger.addHandler(console_handler)

# Функція для логування входу користувачів
def log_user_login(user_id: int, username: str = None, full_name: str = None, action: str = None):
    username_display = f"@{username}" if username else "Unknown"
    full_name_display = full_name if full_name else "Unknown"
    action_display = f", Action: {action}" if action else ""
    user_info = f"User ID: {user_id}, Username: {username_display}, Full Name: {full_name_display}{action_display}"
    login_logger.info(user_info)