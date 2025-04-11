from aiogram import types, Router, F
from database import log_user_visit
from datetime import datetime
from keyboards import main_menu  # Імпортуємо клавіатуру

router = Router()

def get_greeting():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброго ранку"
    elif 12 <= hour < 18:
        return "Доброго дня"
    elif 18 <= hour < 22:
        return "Доброго вечора"
    else:
        return "Доброї ночі"

@router.message(F.text == "/start")
async def start_command(message: types.Message):
    # Логіка вітання
    greeting = get_greeting()
    first_name = message.from_user.first_name
    await message.answer(
        f"{greeting}, {first_name}!\n\n"
        "Потрібна допомога з кондиціонером? Я тут, щоб надати вам всю необхідну інформацію та підтримку.\n\n"
        "Для супроводу у пошуку клікніть потрібну кнопку нижче 👇\n"
        "Для швидкого пошуку просто введіть будь-яку інформацію наприклад:\n"
        "- модель кондиціонера\n"
        "- монтажні розміри\n"
        "- параметри електроживлення\n"
        "- характеристики фреонів\n"
        "- коди помилок",
        reply_markup=main_menu()  # Додаємо клавіатуру
    )
    
    # Логування користувача
    await log_user_visit(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )