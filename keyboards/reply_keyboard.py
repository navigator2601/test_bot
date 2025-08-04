# Файл: keyboards/reply_keyboard.py
# Призначення: Створення та управління Reply-клавіатурами для бота.
# Включає логіку пагінації та фільтрації кнопок за рівнем доступу.

import math
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from common.constants import ALL_MENU_BUTTONS, BUTTONS_PER_PAGE

def _get_filtered_menu_buttons(access_level: int) -> list[str]:
    """
    Фільтрує всі можливі кнопки меню за рівнем доступу користувача.
    Повертає унікальний список текстів кнопок.
    """
    filtered_buttons = []
    seen_buttons = set()
    for button_text, min_level in ALL_MENU_BUTTONS:
        if access_level >= min_level and button_text not in seen_buttons:
            filtered_buttons.append(button_text)
            seen_buttons.add(button_text)
    return filtered_buttons

def get_main_menu_pages_info(access_level: int) -> tuple[int, int]:
    """
    Повертає загальну кількість доступних кнопок та загальну кількість сторінок для головного меню.
    """
    filtered_buttons = _get_filtered_menu_buttons(access_level)
    total_buttons = len(filtered_buttons)
    total_pages = math.ceil(total_buttons / BUTTONS_PER_PAGE) if total_buttons > 0 else 1
    return total_buttons, total_pages

async def get_main_menu_keyboard(access_level: int, page: int = 0) -> ReplyKeyboardMarkup:
    """
    Генерує клавіатуру головного меню з урахуванням рівня доступу та пагінації.
    """
    builder = ReplyKeyboardBuilder()
    unique_buttons_texts = _get_filtered_menu_buttons(access_level)
    total_buttons, total_pages = get_main_menu_pages_info(access_level)
    
    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    buttons_on_page = unique_buttons_texts[start_index:end_index]
    
    for i in range(0, len(buttons_on_page), 2):
        if i + 1 < len(buttons_on_page):
            builder.row(KeyboardButton(text=buttons_on_page[i]), KeyboardButton(text=buttons_on_page[i+1]))
        else:
            builder.row(KeyboardButton(text=buttons_on_page[i]))
            
    pagination_buttons = []
    if total_pages > 1:
        if page > 0:
            pagination_buttons.append(KeyboardButton(text="⬅️ Назад"))
        if page < total_pages - 1:
            pagination_buttons.append(KeyboardButton(text="➡️ Іще"))
    
    if pagination_buttons:
        if len(pagination_buttons) == 1:
            builder.row(pagination_buttons[0])
        else:
            builder.row(*pagination_buttons)
            
    return builder.as_markup(resize_keyboard=True)

# Нова функція для створення клавіатури "Скасувати"
def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Генерує клавіатуру з однією кнопкою "Скасувати"."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Скасувати"))
    return builder.as_markup(resize_keyboard=True)