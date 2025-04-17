from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює головне меню у вигляді клавіатури з 2 стовпчиками.
    Якщо кількість кнопок непарна, остання кнопка займає весь рядок.
    """
    # Список текстів кнопок
    button_texts = [
        "📚 Каталог",
        "📖 Довідник",
        "🕵️ Пошук",
        "🆘 Допомога",
        "⚠️ Коди помилок",
        "🛠️ Технічна інформація",
        "➡️ Додаткові функції"
    ]

    # Формуємо клавіатуру
    keyboard = []
    for i in range(0, len(button_texts) - 1, 2):
        keyboard.append([KeyboardButton(text=button_texts[i]), KeyboardButton(text=button_texts[i + 1])])

    # Додаємо останню кнопку на окремий рядок, якщо кількість кнопок непарна
    if len(button_texts) % 2 != 0:
        keyboard.append([KeyboardButton(text=button_texts[-1])])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )