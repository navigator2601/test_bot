from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command

# Обробник команди /start
async def send_welcome(message: Message):
    await message.answer("Привіт! Я ваш Telegram бот із інтегрованим ШІ!")

# Обробник команди /help
async def send_help(message: Message):
    help_text = (
        "Доступні команди:\n"
        "/start - Почати роботу з ботом\n"
        "/help - Отримати список команд\n"
        "/info - Інформація про бота\n"
        "/settings - Налаштування бота (поки недоступні)"
    )
    await message.answer(help_text)

# Обробник команди /info
async def send_info(message: Message):
    await message.answer("Це Telegram бот із вбудованим штучним інтелектом.")

# Обробник команди /settings
async def send_settings(message: Message):
    await message.answer("Налаштування бота поки що не реалізовані.")

# Обробник текстових повідомлень
async def echo_message(message: Message):
    await message.answer(f"Ви написали: {message.text}")

# Функція для реєстрації обробників команд у диспетчері
def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_help, Command("help"))
    dp.message.register(send_info, Command("info"))
    dp.message.register(send_settings, Command("settings"))
    dp.message.register(echo_message)