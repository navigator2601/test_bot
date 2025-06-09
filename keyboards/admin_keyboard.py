# keyboards/admin_keyboard.py

import math
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.constants import ACCESS_LEVEL_BUTTONS
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Повертає головну клавіатуру адміністратора з оновленими кнопками."""
    buttons = [
        [InlineKeyboardButton(
            text="👥 Юзер-матриця · Редактор доступу",
            callback_data=AdminCallback(action="show_users").pack()
        )],
        [InlineKeyboardButton(
            text="📡 ReLink · Статус каналу зв'язку",
            callback_data=AdminCallback(action="connection_status").pack()
        )],
        [InlineKeyboardButton(
            text="🔐 TeleKey · Авторизація API-зв’язку",
            callback_data=AdminCallback(action="telethon_auth").pack()
        )],
        [InlineKeyboardButton(
            text="💬 Чат-матриця · Перегляд активних зон",
            callback_data=AdminCallback(action="telethon_chats").pack()
        )],
        [InlineKeyboardButton(
            text="🏁 Завершити командування",
            callback_data=AdminCallback(action="close_admin_panel").pack()
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_users_list_keyboard(users: list, current_page: int, users_per_page: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру зі списком користувачів для вибору та пагінації."""
    keyboard = []

    start_index = current_page * users_per_page
    end_index = start_index + users_per_page
    users_on_page = users[start_index:end_index]

    for user in users_on_page:
        user_id = user.get('id')
        if user_id is not None:
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            username = user.get('username', '')
            access_level = user.get('access_level', 0)
            display_name = f"{first_name} {last_name}".strip()
            if not display_name:
                display_name = username or f"ID: {user_id}"
            button_text = f"{display_name} (Рівень: {access_level})"
            # Кнопка користувача через AdminCallback
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=AdminCallback(action="select_user", user_id=user_id).pack()
            )])

    total_pages = math.ceil(len(users) / users_per_page) if len(users) > 0 else 1

    # Додаємо кнопки пагінації
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=AdminCallback(action="show_users", page=current_page - 1).pack()
            )
        )
    pagination_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}",
            callback_data="users_current_page_info" # Цю кнопку не потрібно обробляти як CallbackData, вона просто відображає інфо
        )
    )
    if current_page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=AdminCallback(action="show_users", page=current_page + 1).pack()
            )
        )
    keyboard.append(pagination_buttons)
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="cancel_admin_action").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_user_actions_keyboard(is_authorized: bool, current_access_level: int, user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій з конкретним користувачем."""
    buttons = []
    if is_authorized:
        buttons.append([InlineKeyboardButton(
            text="Деавторизувати ❌",
            callback_data=UserActionCallback(action="unauthorize", user_id=user_id_to_manage).pack()
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="Авторизувати ✅",
            callback_data=UserActionCallback(action="authorize", user_id=user_id_to_manage).pack()
        )])
    buttons.append([InlineKeyboardButton(
        text=f"Змінити рівень доступу ({current_access_level}) ⬆️",
        callback_data=AdminCallback(action="change_access_level", user_id=user_id_to_manage).pack()
    )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад до списку користувачів",
        callback_data=AdminCallback(action="show_users").pack()
    )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад до адмін-меню",
        callback_data=AdminCallback(action="cancel_admin_action").pack()
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_action_keyboard(action: str, user_id: int, level: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Повертає клавіатуру підтвердження дії.
    action: тип дії (наприклад, "authorize", "unauthorize", "set_level")
    user_id: ID користувача, якого стосується дія
    level: новий рівень доступу, якщо дія "set_level"
    """
    buttons = [
        [InlineKeyboardButton(
            text="Підтвердити ✅",
            callback_data=UserActionCallback(action=f"confirm_{action}", user_id=user_id, level=level).pack()
        )],
        [InlineKeyboardButton(
            text="Скасувати ❌",
            callback_data=AdminCallback(action="cancel_action").pack()
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_access_level_keyboard(user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з кнопками для вибору рівня доступу."""
    buttons_flat = []
    for level, name in ACCESS_LEVEL_BUTTONS:
        buttons_flat.append(
            InlineKeyboardButton(
                text=f"{name}",
                callback_data=AccessLevelCallback(level=level, user_id=user_id_to_manage).pack()
            )
        )
    keyboard = [buttons_flat[i:i + 2] for i in range(0, len(buttons_flat), 2)]
    keyboard.append([InlineKeyboardButton(
        text="Скасувати ❌",
        callback_data=AdminCallback(action="select_user", user_id=user_id_to_manage).pack()
    )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_telethon_actions_keyboard() -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій Telethon."""
    buttons = [
        [InlineKeyboardButton(
            text="Перевірити статус Telethon 👁️",
            callback_data=AdminCallback(action="telethon_check_status").pack()
        )],
        [InlineKeyboardButton(
            text="Авторизувати Telethon 🔑",
            callback_data=AdminCallback(action="telethon_start_auth").pack()
        )],
        [InlineKeyboardButton(
            text="Отримати інфо про користувача 🆔",
            callback_data=AdminCallback(action="telethon_get_user_info").pack()
        )],
        [InlineKeyboardButton(
            text="Приєднатися до каналу ➕",
            callback_data=AdminCallback(action="telethon_join_channel").pack()
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="cancel_admin_action").pack()
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)