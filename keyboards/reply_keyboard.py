# keyboards/reply_keyboard.py
# Клавіатури для головного меню
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює головне меню у вигляді клавіатури з динамічним розподілом кнопок.
    """
    buttons = [
        KeyboardButton(text="📚 Каталог"),
        KeyboardButton(text="📖 Довідник"),
        KeyboardButton(text="🕵️ Пошук"),
        KeyboardButton(text="🆘 Допомога"),
        KeyboardButton(text="⚠️ Коди помилок"),
        KeyboardButton(text="🛠️ Технічна інформація"),
        KeyboardButton(text="📐️ Додаткові функції")
    ]

    keyboard = []

    # Додаємо кнопки по 2 в рядок
    for i in range(0, len(buttons) - 1, 2):
        keyboard.append([buttons[i], buttons[i + 1]])

    # Якщо кількість кнопок не парна, додаємо останню кнопку на окремий рядок
    if len(buttons) % 2 != 0:
        keyboard.append([buttons[-1]])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def create_additional_functions_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює додаткову клавіатуру для функцій у форматі основної клавіатури.
    """
    buttons = [
        KeyboardButton(text="🧮 Калькулятор потужності"),
        KeyboardButton(text="📊 Графіки енерговитрат"),
        KeyboardButton(text="📥 Отримати дані з чату"),  # Додана кнопка
        KeyboardButton(text="🔙 Назад до головного меню")
    ]

    keyboard = []

    # Додаємо кнопки по 2 в рядок
    for i in range(0, len(buttons) - 1, 2):
        keyboard.append([buttons[i], buttons[i + 1]])

    # Якщо кількість кнопок не парна, додаємо останню кнопку на окремий рядок
    if len(buttons) % 2 != 0:
        keyboard.append([buttons[-1]])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )