# keyboards/inline_keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import ceil

# Кількість користувачів на одній сторінці для пагінації
USERS_PER_PAGE = 5

async def create_paginated_users_keyboard(users: list[dict], page: int = 1) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру з пагінацією для списку користувачів.
    """
    keyboard_buttons = []
    start_index = (page - 1) * USERS_PER_PAGE
    end_index = start_index + USERS_PER_PAGE

    # Отримуємо користувачів для поточної сторінки
    users_on_page = users[start_index:end_index]

    for user in users_on_page:
        user_id = user['id']
        username = user.get('username', 'N/A')
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')

        user_info = f"{first_name} {last_name}".strip() or username # Використовуємо ім'я/прізвище або нік
        if username and user_info != username: # Додаємо нік, якщо він є і відрізняється від імені
            user_info = f"{user_info} (@{username})"

        # Додаємо кнопку для кожного користувача
        keyboard_buttons.append([
            InlineKeyboardButton(text=user_info, callback_data=f"user_select:{user_id}")
        ])

    # Додаємо кнопки навігації
    total_users = len(users)
    total_pages = ceil(total_users / USERS_PER_PAGE)

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"users_page:{page-1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"users_page:{page+1}"))
    
    if navigation_buttons:
        keyboard_buttons.append(navigation_buttons)
    
    # Додаємо кнопки "Назад до адмін-панелі" та "Закрити"
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ До адмін-панелі", callback_data="back_to_admin_panel"),
        InlineKeyboardButton(text="Закрити ❌", callback_data="close_menu") # Виправлено callback_data на "close_menu"
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

async def create_user_management_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для керування конкретним користувачем.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Авторизувати ✅", callback_data=f"authorize_user:{target_user_id}")],
        [InlineKeyboardButton(text="Деавторизувати ❌", callback_data=f"deauthorize_user:{target_user_id}")],
        [InlineKeyboardButton(text="Змінити рівень доступу ⚙️", callback_data=f"change_access:{target_user_id}")],
        [InlineKeyboardButton(text="⬅️ Назад до списку", callback_data="back_to_users_list")], # Виправлено callback_data на "back_to_users_list"
        [InlineKeyboardButton(text="Закрити ❌", callback_data="close_menu")] # Додано кнопку "Закрити"
    ])
    return keyboard