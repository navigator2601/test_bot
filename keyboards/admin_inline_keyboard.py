# Файл: keyboards/admin_inline_keyboard.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# --- КЛАВІАТУРА 1: Вибір Додати/Редагувати ---
def get_db_operations_start_keyboard() -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру для вибору початкової операції
    керування БД: Редагування або Додавання.
    """
    logger.debug("Генерація інлайн-клавіатури для вибору DB операції: Редагувати/Додати/Скасувати.")
    
    keyboard_buttons = [
        # Ряд 1: Операції
        [
            InlineKeyboardButton(text="✍️ Редагувати дані", callback_data="db_op_edit"),
            InlineKeyboardButton(text="➕ Додати дані", callback_data="db_op_add")
        ],
        # Ряд 2: Скасування
        [
            InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_admin_op")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- КЛАВІАТУРА 2: Вибір об'єкта Редагування ---
def get_db_operations_edit_category_keyboard() -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру для вибору об'єкта редагування: Бренди/Серії або Моделі.
    """
    logger.debug("Генерація інлайн-клавіатури для вибору категорії редагування: Бренди/Моделі.")
    
    keyboard_buttons = [
        # Ряд 1: Вибір об'єкта
        [
            InlineKeyboardButton(text="🏭 Редагувати Бренди/Серії", callback_data="db_edit_brands"),
        ],
        [
            InlineKeyboardButton(text="❄️ Редагувати Моделі", callback_data="db_edit_models"),
        ],
        # Ряд 2: Навігація
        [
            InlineKeyboardButton(text="↩️ Назад (Вибір операції)", callback_data="db_op_start"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_admin_op")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- 🔥 КЛАВІАТУРА 3: Вибір Бренду/Серії для редагування ---
def get_admin_brand_series_selection_keyboard(brands_data: List[Dict]) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру зі списком брендів/серій та їхнім % наповнення.
    brands_data очікується як результат запиту, наприклад:
    [{'brand_name': 'Gree', 'series_name_ukr': 'Bora', 'completeness_percent': 75.5, 'series_id': 1}, ...]
    """
    logger.debug(f"Генерація клавіатури вибору брендів. Кількість елементів: {len(brands_data)}")
    
    keyboard_buttons = []

    # Додавання кнопок для кожного бренду/серії
    for item in brands_data:
        # 🔥 Використовуємо імена полів з вашого SQL-запиту 🔥
        brand_name = item.get('brand_name', 'N/A')
        series_name = item.get('series_name_ukr', 'N/A')
        fill_percent = int(item.get('completeness_percent', 0))
        series_id = item.get('series_id')
        
        # Перевірка наявності ID (якщо запит повернув NULL, що небажано)
        if series_id is None:
            logger.warning(f"Пропущено серію {brand_name}:{series_name} через відсутність series_id.")
            continue

        # Формат: Бренд: Серія - %
        text = f"🏭 {brand_name}: {series_name} - {fill_percent}%"
        # callback_data: db_edit_series_select:1 (де 1 - це series_id)
        callback_data = f"db_edit_series_select:{series_id}" 
        
        keyboard_buttons.append(
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        )

    # Додавання службових кнопок в кінці
    service_buttons = [
        # Кнопка для додавання нового бренду
        [InlineKeyboardButton(text="➕ Додати новий Бренд/Серію", callback_data="db_add_new_brand_series")],
        # Навігація
        [
            InlineKeyboardButton(text="↩️ Назад (Вибір об'єкта)", callback_data="db_op_edit"),
            InlineKeyboardButton(text="❌ Скасувати (Вихід)", callback_data="cancel_admin_op")
        ]
    ]
    
    keyboard_buttons.extend(service_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)