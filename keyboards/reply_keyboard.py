from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram import Router
from utils.logger import setup_logger

# Ініціалізація логера
logger = setup_logger("reply_keyboard_logger")

# Ініціалізація роутера
router = Router()

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює головне меню у вигляді клавіатури з автоматичним формуванням рядків.
    Якщо кількість кнопок непарна, остання кнопка займає весь рядок.
    """
    # Список текстів кнопок для головного меню
    button_texts = [
        "📚 Каталог",                # Каталог доступних кондиціонерів
        "📖 Довідник",               # Довідкові матеріали
        "🕵️ Пошук",                  # Інтелектуальний пошук
        "🆘 Допомога",               # Опис функціоналу
        "⚠️ Коди помилок",           # Інформація про коди помилок
        "🛠️ Технічна інформація",    # Інформація про монтаж
        "📐️ Додаткові функції"        # Перехід до калькуляторів та інших функцій
    ]

    # Формування клавіатури: 2 кнопки в рядку
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

def create_additional_functions_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює клавіатуру для додаткових функцій у форматі 2 стовпці.
    Якщо кількість кнопок непарна, остання кнопка займає весь рядок.
    """
    # Список текстів кнопок для додаткових функцій
    button_texts = [
        "🧮 Калькулятор потужності",  # Розрахунок необхідної потужності кондиціонера
        "📊 Графіки енерговитрат",   # Візуалізація енерговитрат
        "🔙 Назад до головного меню"  # Повернення до головного меню
    ]

    # Формування клавіатури: 2 кнопки в рядку
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

def get_all_button_texts() -> list:
    """
    Отримує список текстів усіх кнопок, які є в головному меню та додаткових функціях.
    """
    main_menu_buttons = create_main_menu_keyboard().keyboard
    additional_menu_buttons = create_additional_functions_keyboard().keyboard
    all_buttons = main_menu_buttons + additional_menu_buttons
    return [button.text for row in all_buttons for button in row]

# Обробники для кнопок
@router.message(lambda message: message.text == "➡️ Додаткові функції")
async def show_additional_functions(message: Message):
    """
    Обробник для кнопки "➡️ Додаткові функції".
    """
    await message.answer(
        "Ви в розділі додаткових функцій, оберіть що вас цікавить.",
        reply_markup=create_additional_functions_keyboard()
    )

@router.message(lambda message: message.text == "🔙 Назад до головного меню")
async def back_to_main_menu(message: Message):
    """
    Обробник для кнопки "🔙 Назад до головного меню".
    """
    await message.answer(
        "Ви повернулися в головне меню:",
        reply_markup=create_main_menu_keyboard()
    )

@router.message(lambda message: message.text in get_all_button_texts())
async def log_button_click(message: Message):
    """
    Логування натискання кнопок.
    """
    user = message.from_user
    logger.info(f"Користувач {user.full_name} (@{user.username}) (ID: {user.id}) натиснув кнопку '{message.text}'.")
    await message.answer(f"Ви перейшли до розділу: {message.text}")