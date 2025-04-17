from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює головне меню у вигляді клавіатури з динамічним розподілом кнопок на 2 стовпчики.
    Якщо кількість кнопок не парна, остання кнопка займає ширину 2-х колонок.
    """
    # Список кнопок для меню з піктограмами
    buttons = [
        KeyboardButton(text="📚 Каталог"),
        KeyboardButton(text="📖 Довідник"),
        KeyboardButton(text="🕵️ Пошук"),
        KeyboardButton(text="🆘 Допомога"),
        KeyboardButton(text="⚠️ Коди помилок"),  # Нова кнопка
        KeyboardButton(text="❓ FAQ"),           # Нова кнопка
        KeyboardButton(text="⚙️ Технічна інформація")  # Нова кнопка
    ]

    # Створюємо клавіатуру
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