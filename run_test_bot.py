import os
import sys

# Додавання шляху до поточної директорії для пошуку модулів
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Завантаження конфігурації для тестового середовища
os.environ['ENV_FILE'] = '.env.test'

from bot import Bot

# Ініціалізація бота з тестовими налаштуваннями
bot = Bot()

if __name__ == "__main__":
    bot.run()