# config.py

import os
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env
load_dotenv()

# Отримання токена бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Налаштування бази даних PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Ключ API для OpenWeatherMap або аналогічного сервісу
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Налаштування Telethon API (для взаємодії з Telegram як користувач)
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')

# ID адміністратора Telegram
ADMIN_ID = int(os.getenv('ADMIN_ID'))

# Перевірка, що всі необхідні змінні завантажені
if not all([BOT_TOKEN, DATABASE_URL, WEATHER_API_KEY, API_ID, API_HASH, TELEGRAM_PHONE, ADMIN_ID]):
    raise EnvironmentError("Не всі необхідні змінні оточення завантажені. Перевірте файл .env")

# Шляхи до файлів логів (для використання в logger.py)
LOGS_DIR = 'logs'
BOT_LOG_FILE = os.path.join(LOGS_DIR, 'bot.log')
LAST_LOGIN_LOG_FILE = os.path.join(LOGS_DIR, 'last_login.log')

# Створюємо директорію для логів, якщо її немає
os.makedirs(LOGS_DIR, exist_ok=True)

print("Конфігурацію завантажено успішно.")