from aiogram import types
from aiogram import Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm import Session
from database import SessionLocal, log_user_action

async def user_command(message: types.Message):
    db: Session = SessionLocal()
    log_user_action(db, message.from_user.id, "user_command")
    await message.reply("This is a user command response.")

def register_handlers_user(dp: Dispatcher):
    dp.message.register(user_command, Command(commands=["user"]))