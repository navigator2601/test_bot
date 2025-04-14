# Обробник команди /start
from aiogram import Router, types
from aiogram.filters import Command  # Використання нового способу фільтрації команд
from datetime import datetime

# Ініціалізація роутера
router = Router()

# Функція визначення привітання відповідно до часу доби
def get_greeting() -> str:
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 23:
        return "Доброго вечора"
    else:
        return "Доброї ночі"

# Обробник команди /start
@router.message(Command(commands=["start"]))  # Використовуємо новий спосіб фільтрації
async def start_command_handler(message: types.Message):
    user_name = message.from_user.first_name
    greeting = get_greeting()
    await message.answer(f"{greeting}, {user_name}!")
    await message.answer("Для супроводу у пошуку клікніть потрібну кнопку нижче 👇\n"
                         "Для швидкого пошуку просто введіть будь-яку інформацію")

# Функція реєстрації роутера
def register_start_handler(dp):
    dp.include_router(router)
