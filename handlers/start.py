from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

async def start_command_handler(message: Message):
    await message.answer("Hello! I'm your bot.")

def register_handlers_start(router: Router):
    router.message.register(start_command_handler, Command("start"))