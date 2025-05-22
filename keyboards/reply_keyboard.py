# keyboards/reply_keyboard.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.logger import logger
import math # Хоча ви використовуєте цілочисельне ділення, math.ceil краще для ясності пагінації

module_logger = logger.getChild(__name__)

# Визначення всіх можливих кнопок з їх мінімальним рівнем доступу
# Використовуємо словник для зручності доступу за рівнем доступу
# і для легшого розширення
BUTTONS_CONFIG = {
    0: [ # Базовий рівень доступу
        ("📚 Каталог", 0),
        ("📖 Довідники", 0),
        ("🕵️ Пошук", 0),
        ("⚠️ Коди помилок", 0),
        ("🛠️ Інструкції", 0),
        ("📐 Додаткові функції", 0),
    ],
    1: [ # Рівень доступу 1 (додаткові кнопки)
        ("📚 Каталог", 0),
        ("📖 Довідники", 0),
        ("🕵️ Пошук", 0),
        ("⚠️ Коди помилок", 0),
        ("🛠️ Інструкції", 0),
        ("📐 Додаткові функції", 0),
        ("🅰️ Пошук магазинів", 1),
        ("🔄 Отримати список ТТ", 1),
        ("📝 Завдання в роботі", 1),
        ("🧾 Звіт по роботі", 1),
    ],
    10: [ # Рівень доступу 10 (адмінські кнопки)
        ("📚 Каталог", 0),
        ("📖 Довідники", 0),
        ("🕵️ Пошук", 0),
        ("⚠️ Коди помилок", 0),
        ("🛠️ Інструкції", 0),
        ("📐 Додаткові функції", 0),
        ("🅰️ Пошук магазинів", 1),
        ("🔄 Отримати список ТТ", 1),
        ("📝 Завдання в роботі", 1),
        ("🧾 Звіт по роботі", 1),
        ("⚙️ Адміністрування", 10),
    ]
    # Додайте інші рівні доступу та їхні кнопки тут за потребою
}

BUTTONS_PER_PAGE = 6 # Максимум 3 ряди по 2 кнопки

def get_total_pages(user_access_level: int) -> int:
    """
    Розраховує загальну кількість сторінок для даного рівня доступу.
    Ця функція потрібна для імпорту в handler'ах.
    """
    # Фільтруємо кнопки за рівнем доступу користувача
    available_buttons_data = BUTTONS_CONFIG.get(user_access_level)
    if available_buttons_data is None:
        # Якщо рівень доступу не знайдено, спробуйте базовий рівень 0
        available_buttons_data = BUTTONS_CONFIG.get(0, [])
        module_logger.warning(f"Рівень доступу {user_access_level} не знайдено. Використано базові кнопки.")

    available_buttons_text = [text for text, _ in available_buttons_data if user_access_level >= _]
    
    total_buttons = len(available_buttons_text)
    if total_buttons == 0:
        return 0
    return math.ceil(total_buttons / BUTTONS_PER_PAGE)


def create_paginated_keyboard(page: int = 1, user_access_level: int = 0) -> ReplyKeyboardMarkup:
    # ДОДАНО ЛОГУВАННЯ ДЛЯ НАЛАГОДЖЕННЯ
    module_logger.debug(f"Виклик create_paginated_keyboard: page={page}, access_level={user_access_level}")
    
    # 1. Фільтруємо кнопки за рівнем доступу користувача
    available_buttons_data = BUTTONS_CONFIG.get(user_access_level)
    if available_buttons_data is None:
        # Якщо рівень доступу не знайдено, спробуйте базовий рівень 0
        available_buttons_data = BUTTONS_CONFIG.get(0, [])
        module_logger.warning(f"Рівень доступу {user_access_level} не знайдено. Використано базові кнопки.")

    available_buttons_text = [text for text, required_level in available_buttons_data if user_access_level >= required_level]
    
    # ДОДАНО ЛОГУВАННЯ
    module_logger.debug(f"Доступні кнопки для access_level {user_access_level}: {available_buttons_text}")

    total_buttons = len(available_buttons_text)
    # Змінено на math.ceil для коректного розрахунку сторінок
    total_pages = math.ceil(total_buttons / BUTTONS_PER_PAGE) if total_buttons > 0 else 0

    # ДОДАНО ЛОГУВАННЯ
    module_logger.debug(f"Всього доступних кнопок: {total_buttons}, Всього сторінок: {total_pages}")

    # Обробка некоректного номера сторінки
    if total_pages == 0: 
        page = 0 
    elif page > total_pages:
        # ДОДАНО ЛОГУВАННЯ
        module_logger.warning(f"Запитувана сторінка {page} виходить за межі ({total_pages} сторінок). Перехід на останню.")
        page = total_pages 
    elif page < 1:
        # ДОДАНО ЛОГУВАННЯ
        module_logger.warning(f"Запитувана сторінка {page} менше 1. Перехід на першу.")
        page = 1 
    
    # ДОДАНО ЛОГУВАННЯ
    module_logger.debug(f"Підсумкова сторінка для відображення: {page}")

    if page == 0:
        # ДОДАНО ЛОГУВАННЯ
        module_logger.debug("Кнопок немає, повертаю порожню клавіатуру.")
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True, one_time_keyboard=False)

    start_index = (page - 1) * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    
    # Кнопки для поточної сторінки
    current_page_buttons = available_buttons_text[start_index:end_index]
    # ДОДАНО ЛОГУВАННЯ
    module_logger.debug(f"Кнопки для поточної сторінки {page}: {current_page_buttons}")
    
    # Формуємо ряди по 2 кнопки
    rows = []
    for i in range(0, len(current_page_buttons), 2):
        rows.append([KeyboardButton(text=text) for text in current_page_buttons[i:i + 2]])

    # Додаємо кнопки навігації (⬅️ Назад, ➡️ Іще)
    navigation_row = []
    if page > 1:
        navigation_row.append(KeyboardButton(text="⬅️ Назад"))
    
    # Кнопка "Головна" тепер не додається автоматично у пагінації.
    # Якщо вам потрібна кнопка "Головна" для повернення з інших сценаріїв (не пагінації),
    # ви можете додавати її окремо в цих сценаріях.

    if page < total_pages:
        navigation_row.append(KeyboardButton(text="➡️ Іще"))
    if navigation_row:
        # Додаємо навігаційну кнопку(и) в окремий рядок.
        rows.append(navigation_row)
        # ДОДАНО ЛОГУВАННЯ
        module_logger.debug(f"Додана навігаційна кнопка(и): {[b.text for b in navigation_row]}")
    else:
        # ДОДАНО ЛОГУВАННЯ
        module_logger.debug("Навігаційні кнопки не додано.")

    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=False)
    return keyboard