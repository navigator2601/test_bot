from aiogram import Bot
from config import BOT_TOKEN
import asyncio

# Функція для отримання команд
async def get_bot_commands():
    bot = Bot(token=BOT_TOKEN)
    commands = await bot.get_my_commands()
    if commands:
        print("Встановлені команди:")
        for command in commands:
            print(f"/{command.command} - {command.description}")
    else:
        print("Команди не встановлено.")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(get_bot_commands())