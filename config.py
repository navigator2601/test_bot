# config.py
import os
from dotenv import load_dotenv

load_dotenv() # Завантажує змінні з .env файлу

# Обов'язкові змінні для бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# URL бази даних
DATABASE_URL = os.getenv("DATABASE_URL")

# API-ключ для погоди
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Дані для Telethon
TELETHON_API_ID = os.getenv("API_ID")
TELETHON_API_HASH = os.getenv("API_HASH")
TELETHON_PHONE = os.getenv("TELEGRAM_PHONE")
TELETHON_SESSION_NAME = 'kondiki_reader'

# Налаштування для Google Drive API (Service Account) - ЗАЛИШАЄМО
# Вони можуть бути відсутніми, поки ви не почнете розробляти відповідний функціонал
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY_FILE = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY_FILE") # Прибираємо значення за замовчуванням
GOOGLE_DRIVE_LOGS_FOLDER_ID = os.getenv("GOOGLE_DRIVE_LOGS_FOLDER_ID")

# Перевірка наявності обов'язкових змінних для БОТА та TELETHON
if not BOT_TOKEN:
    raise ValueError("Необхідно вказати BOT_TOKEN у файлі .env")
if not DATABASE_URL:
    raise ValueError("Необхідно вказати DATABASE_URL у файлі .env")
if not WEATHER_API_KEY:
    raise ValueError("Необхідно вказати WEATHER_API_KEY у файлі .env")

# Перевірки для Telethon
if not TELETHON_API_ID:
    raise ValueError("Необхідно вказати API_ID у файлі .env")
if not TELETHON_API_HASH:
    raise ValueError("Необхідно вказати API_HASH у файлі .env")
if not TELETHON_PHONE:
    raise ValueError("Необхідно вказати TELEGRAM_PHONE у файлі .env")

# Перетворення на правильні типи даних
try:
    ADMIN_ID = int(ADMIN_ID)
    TELETHON_API_ID = int(TELETHON_API_ID)
except (ValueError, TypeError) as e:
    raise ValueError(f"Invalid format for ADMIN_ID or API_ID in .env: {e}. Ensure they are integers.")

# Додаємо змінну, яка показує, чи доступні налаштування Google Drive
# Це дозволить іншим модулям перевіряти, чи можна використовувати Google Drive
GOOGLE_DRIVE_ENABLED = bool(GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY_FILE and GOOGLE_DRIVE_LOGS_FOLDER_ID)

if GOOGLE_DRIVE_ENABLED:
    print("Google Drive інтеграція увімкнена. Переконайтеся, що файл ключів та ID папки коректні.")
else:
    print("Google Drive інтеграція вимкнена. Змінні GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY_FILE та/або GOOGLE_DRIVE_LOGS_FOLDER_ID відсутні.")