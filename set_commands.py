from aiogram import Bot
from aiogram.types import BotCommand
import asyncio
from config import BOT_TOKEN

# Налаштування команд
async def set_bot_commands():
    bot = Bot(token=BOT_TOKEN)
    commands = [
        BotCommand(command="start", description="Почати роботу з ботом"),
        BotCommand(command="help", description="Список доступних функцій"),
        BotCommand(command="info", description="Інформація про бота"),
    ]
    await bot.set_my_commands(commands)
    print("Меню команд успішно встановлено!")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(set_bot_commands())