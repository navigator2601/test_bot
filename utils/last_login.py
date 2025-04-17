import os
from datetime import datetime

# Шлях до файлу для збереження логів
LOGS_DIR = os.path.join(os.path.dirname(__file__), "../logs")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "last_login.log")

# Переконаємося, що папка logs існує
os.makedirs(LOGS_DIR, exist_ok=True)

def log_user_login(user_id: int, username: str, full_name: str):
    """
    Записує інформацію про вхід користувача у файл.

    :param user_id: Унікальний ID користувача.
    :param username: Ім'я користувача в Telegram.
    :param full_name: Повне ім'я користувача.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User ID: {user_id}, Username: @{username}, Full Name: {full_name}\n"

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)