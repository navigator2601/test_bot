import os
import psycopg2
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from transformers import pipeline

# Завантаження даних з файлу .env
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Налаштування з'єднання з базою даних
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Ініціалізація бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Ініціалізація моделі LLaMA через Hugging Face
generator = pipeline('text-generation', model='meta-llama/Meta-Llama-3-8B')

# Обробка команди /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт! Я бот для роботи з базою даних PostgreSQL. Введіть свій запит.")

# Обробка повідомлень від користувача
@dp.message_handler()
async def handle_query(message: types.Message):
    user_query = message.text
    response = generator(user_query, max_length=150, num_return_sequences=1)
    sql_query = response[0]['generated_text']
    
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        await message.reply(f"Результат запиту:\n{result}")
    except Exception as e:
        await message.reply(f"Помилка при виконанні запиту:\n{e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)