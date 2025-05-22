# handlers/menu_handler.py

from aiogram import Router
from aiogram.types import BotCommand

# Ініціалізація роутера для цього модуля
router = Router(name="Обробник переходів між меню")

async def set_main_menu(bot):
    """
    Встановлює головне меню команд.
    """
    commands = [
        BotCommand(command="/start", description="Запустити бота"),
        BotCommand(command="/help", description="Допомога по використанню бота"),  # Додано
        BotCommand(command="/info", description="Отримати інформацію про бота"),  # Додано
        BotCommand(command="/find", description="Пошук інформації"),  # Додано
    ]
    await bot.set_my_commands(commands)