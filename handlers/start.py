from aiogram import types
from aiogram import Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm import Session
from database import SessionLocal, create_user, get_user, log_user_action, User
from datetime import datetime
from openai_utils import get_ai_response

def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 22:
        return "Доброго вечора"
    else:
        return "Доброї ночі"

async def start_command(message: types.Message):
    db: Session = SessionLocal()
    user = get_user(db, message.from_user.id)
    if not user:
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        create_user(db, user)
    log_user_action(db, user.id, "start_command")

    greeting = get_greeting()
    user_name = message.from_user.first_name or message.from_user.username
    welcome_text = f"{greeting}, {user_name}!\n\nДля супроводу натисніть потрібну кнопку внизу.\nДля швидкого пошуку просто введіть будь-яку інформацію:\n- Модель кондиціонера\n- Потужність кондиціонера\n- Розміри блоків\n- Типи кондиціонерів\nАбо іншу інформацію яка цікавить"

    await message.reply(welcome_text)

    # Використання OpenAI для генерації додаткового повідомлення
    ai_response = get_ai_response("Привітання для користувача")
    await message.reply(ai_response)

def register_handlers_start(dp: Dispatcher):
    dp.message.register(start_command, Command(commands=["start"]))