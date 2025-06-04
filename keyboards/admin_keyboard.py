from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import ceil

from common.constants import ACCESS_LEVEL_BUTTONS
from keyboards.callback_factories import AdminCallback

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
            callback_data="close_admin_panel"
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

    total_pages = ceil(len(users) / users_per_page) if len(users) > 0 else 1

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
            callback_data="users_current_page_info"
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
            callback_data="cancel_admin_action"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_user_actions_keyboard(is_authorized: bool, current_access_level: int, user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій з конкретним користувачем."""
    buttons = []
    if is_authorized:
        buttons.append([InlineKeyboardButton(
            text="Деавторизувати ❌",
            callback_data=f"unauthorize_user_{user_id_to_manage}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="Авторизувати ✅",
            callback_data=f"authorize_user_{user_id_to_manage}"
        )])
    buttons.append([InlineKeyboardButton(
        text=f"Змінити рівень доступу ({current_access_level}) ⬆️",
        callback_data=f"change_access_level_{user_id_to_manage}"
    )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад до списку користувачів",
        callback_data=AdminCallback(action="show_users").pack()
    )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад до адмін-меню",
        callback_data="cancel_admin_action"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_action_keyboard(action_data: str) -> InlineKeyboardMarkup:
    """Повертає клавіатуру підтвердження дії."""
    buttons = [
        [InlineKeyboardButton(text="Підтвердити ✅", callback_data=f"confirm_{action_data}")],
        [InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_access_level_keyboard(user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з кнопками для вибору рівня доступу."""
    buttons_flat = []
    for level, name in ACCESS_LEVEL_BUTTONS:
        buttons_flat.append(
            InlineKeyboardButton(
                text=f"{name}",
                callback_data=f"set_access_level_{level}_{user_id_to_manage}"
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
            callback_data="telethon_check_status"
        )],
        [InlineKeyboardButton(
            text="Авторизувати Telethon 🔑",
            callback_data="telethon_start_auth"
        )],
        [InlineKeyboardButton(
            text="Отримати інфо про користувача 🆔",
            callback_data="telethon_get_user_info"
        )],
        [InlineKeyboardButton(
            text="Приєднатися до каналу ➕",
            callback_data="telethon_join_channel"
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data="cancel_admin_action"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)