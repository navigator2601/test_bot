import os
from bot import Bot

# Завантаження конфігурації для тестового середовища
os.environ['ENV_FILE'] = '.env.test'

# Ініціалізація бота з тестовими налаштуваннями
bot = Bot()

if __name__ == "__main__":
    bot.run()