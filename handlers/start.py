from aiogram import types, Router, F
from keyboards import main_menu
from datetime import datetime

router = Router()

# Привітання залежно від часу
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
    """Обробник для команди /start"""
    greeting = get_greeting()
    first_name = message.from_user.first_name  # Отримуємо ім'я користувача
    await message.answer(
        f"<b>{greeting}, {first_name}!</b>\n\n"
        "Потрібна допомога з кондиціонером? Я тут, щоб надати вам всю необхідну інформацію та підтримку.\n\n"
        "Для супроводу у пошуку клікніть потрібну кнопку нижче 👇\n"
        "Для швидкого пошуку просто введіть будь-яку інформацію, наприклад:\n"
        "- модель кондиціонера\n"
        "- монтажні розміри\n"
        "- параметри електроживлення\n"
        "- характеристики фреонів\n"
        "- коди помилок\n",
        reply_markup=main_menu(),  # Відображення головного меню
        parse_mode="HTML"  # Використовуємо HTML для форматування
    )