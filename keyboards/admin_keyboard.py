# keyboards/admin_keyboard.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює клавіатуру для адміністративного меню.
    """
    keyboard = [
        [KeyboardButton(text="👥 Користувачі"), KeyboardButton(text="📊 Статус підключення")], 
        [KeyboardButton(text="📝 Подивитися логи"), KeyboardButton(text="🚀 Авторизувати Telethon")],
        [KeyboardButton(text="↩️ Головне меню")] # Кнопка повернення до головного меню
    ]
    # resize_keyboard=True робить клавіатуру меншою, one_time_keyboard=False залишає її видимою
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)