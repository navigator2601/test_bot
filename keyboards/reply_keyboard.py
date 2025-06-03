# keyboards/reply_keyboard.py

import math
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Конфігурація кнопок за рівнями доступу
# Кожен елемент кортежу: (Текст кнопки, Мінімальний рівень доступу для кнопки)
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

BUTTONS_PER_PAGE = 6 # Максимум 3 ряди по 2 кнопки, якщо кнопок більше чим 6 то розділяти клавіатуру на сторінки

async def get_main_menu_keyboard(access_level: int = 0, page: int = 0) -> ReplyKeyboardMarkup:
    """
    Генерує клавіатуру головного меню з урахуванням рівня доступу та пагінації.

    :param access_level: Рівень доступу користувача.
    :param page: Поточна сторінка клавіатури (0-індексована).
    :return: Об'єкт ReplyKeyboardMarkup.
    """
    builder = ReplyKeyboardBuilder()

    # Отримуємо всі унікальні кнопки, доступні для даного рівня доступу
    # Зберігаємо лише текст кнопки, щоб уникнути дублікатів (наприклад, "Каталог" з level 0 і level 1)
    unique_buttons_texts = []
    for level in sorted(BUTTONS_CONFIG.keys()): # Сортуємо рівні, щоб базові кнопки додавалися першими
        if access_level >= level:
            for button_text, min_level in BUTTONS_CONFIG[level]:
                if access_level >= min_level and button_text not in unique_buttons_texts:
                    unique_buttons_texts.append(button_text)
    
    # Визначаємо загальну кількість сторінок
    total_buttons = len(unique_buttons_texts)
    total_pages = math.ceil(total_buttons / BUTTONS_PER_PAGE) if total_buttons > 0 else 1

    # Визначаємо кнопки для поточної сторінки
    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    buttons_on_page = unique_buttons_texts[start_index:end_index]

    # Додаємо кнопки до клавіатури, по 2 в ряд
    for i in range(0, len(buttons_on_page), 2):
        if i + 1 < len(buttons_on_page):
            builder.row(KeyboardButton(text=buttons_on_page[i]), KeyboardButton(text=buttons_on_page[i+1]))
        else: # Якщо непарна кількість кнопок, остання кнопка займає весь ряд
            builder.row(KeyboardButton(text=buttons_on_page[i]))

    # Додаємо кнопки пагінації
    pagination_buttons = []
    if total_pages > 1: # Пагінація потрібна, тільки якщо є більше однієї сторінки
        if page > 0:
            pagination_buttons.append(KeyboardButton(text="⬅️ Назад"))
        if page < total_pages - 1:
            pagination_buttons.append(KeyboardButton(text="➡️ Іще"))

    if pagination_buttons:
        # Якщо кнопок пагінації одна (лише "Іще" або "Назад"), то вона займає весь ряд
        if len(pagination_buttons) == 1:
            builder.row(pagination_buttons[0])
        else: # Якщо дві кнопки пагінації, вони в одному ряду
            builder.row(*pagination_buttons)

    return builder.as_markup(resize_keyboard=True)

if __name__ == '__main__':
    # Цей блок дозволяє тестувати генерацію клавіатури окремо, запустивши цей файл
    # python keyboards/reply_keyboard.py
    async def test_keyboard_generation():
        print("--- Тестування клавіатур ---")

        print("\nДля access_level=0, page=0 (базовий рівень, перша сторінка)")
        kb0_0 = await get_main_menu_keyboard(access_level=0, page=0)
        print(kb0_0.keyboard)

        print("\nДля access_level=1, page=0 (рівень 1, перша сторінка)")
        kb1_0 = await get_main_menu_keyboard(access_level=1, page=0)
        print(kb1_0.keyboard)

        print("\nДля access_level=1, page=1 (рівень 1, друга сторінка)")
        kb1_1 = await get_main_menu_keyboard(access_level=1, page=1)
        print(kb1_1.keyboard)
        
        print("\nДля access_level=10, page=0 (адмінський рівень, перша сторінка)")
        kb10_0 = await get_main_menu_keyboard(access_level=10, page=0)
        print(kb10_0.keyboard)

        print("\nДля access_level=10, page=1 (адмінський рівень, друга сторінка)")
        kb10_1 = await get_main_menu_keyboard(access_level=10, page=1)
        print(kb10_1.keyboard)

    import asyncio
    asyncio.run(test_keyboard_generation())