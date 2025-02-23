import os
from dotenv import load_dotenv

# Завантаження конфігурації з відповідного файлу
env_file = os.getenv('ENV_FILE', '.env')
load_dotenv(env_file)

# Загальні налаштування
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')