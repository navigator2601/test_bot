# keyboards/admin_keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import ceil

# Конфігурація для кнопок рівня доступу (для використання в адмін-панелі)
ACCESS_LEVEL_BUTTONS = [
    (0, "🔒 Гість [Level 0]"),
    (1, "🧭 Техно-Навігатор [L1]"),
    (3, "🔧 Системний Інженер [L3]"),
    (6, "📊 Керівник Протоколів [L6]"),
    (10, "🛡️ Адміністратор Ядра [L10]"),
    (100, "🧬 Архітектор Системи [ROOT]"),
    (101, "🌀 Пробуджений Refridex [L∞]")  # Таємний рівень
]

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Повертає головну клавіатуру адміністратора з оновленими кнопками."""
    buttons = [
        [InlineKeyboardButton(text="👥 Юзер-матриця · Редактор доступу", callback_data="admin_show_users")],
        [InlineKeyboardButton(text="📡 ReLink · Статус каналу зв'язку", callback_data="admin_connection_status")],
        [InlineKeyboardButton(text="🔐 TeleKey · Авторизація API-зв’язку", callback_data="admin_telethon_auth")],
        [InlineKeyboardButton(text="💬 Чат-матриця · Перегляд активних зон", callback_data="admin_telethon_chats")],
        [InlineKeyboardButton(text="🏁 Завершити командування", callback_data="close_admin_panel")]
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
            access_level = user.get('access_level', 0)
            
            # Формуємо текст кнопки з first_name, last_name та access_level
            button_text = f"{first_name} {last_name} (Рівень: {access_level})"
            # Callback_data залишаємо user_{user_id} для вибору користувача
            keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"user_{user_id}")])

    total_pages = ceil(len(users) / users_per_page) if len(users) > 0 else 1

    # Додаємо кнопки пагінації
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{current_page - 1}"))
    
    # Кнопка поточної сторінки
    pagination_buttons.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="current_page_info"))
    
    if current_page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{current_page + 1}"))
    
    keyboard.append(pagination_buttons)
    # Кнопка "Назад до адмін-меню"
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад до адмін-меню", callback_data="cancel_admin_action")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Генерує клавіатуру пагінації для списку користувачів.
    Ця функція може бути використана, якщо пагінація потрібна окремо.
    """
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{current_page - 1}"))
    
    buttons.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="current_page_display"))

    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{current_page + 1}"))
    
    # Додаємо кнопку повернення
    back_button = [InlineKeyboardButton(text="⬅️ Назад до адмін-меню", callback_data="cancel_admin_action")]
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons, back_button])


def get_user_actions_keyboard(is_authorized: bool, current_access_level: int, user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій з конкретним користувачем."""
    buttons = []
    if is_authorized:
        buttons.append([InlineKeyboardButton(text="Деавторизувати ❌", callback_data=f"unauthorize_user_{user_id_to_manage}")])
    else:
        buttons.append([InlineKeyboardButton(text="Авторизувати ✅", callback_data=f"authorize_user_{user_id_to_manage}")])
    
    buttons.append([InlineKeyboardButton(text=f"Змінити рівень доступу ({current_access_level}) ⬆️", callback_data=f"change_access_level_{user_id_to_manage}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад до списку користувачів", callback_data="admin_show_users")]) # Повернутись до списку
    buttons.append([InlineKeyboardButton(text="⬅️ Назад до адмін-меню", callback_data="cancel_admin_action")]) # Повернутись до головного адмін-меню
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
    buttons = []
    for level, name in ACCESS_LEVEL_BUTTONS:
        # Змінюємо формат тексту кнопки: числове значення на початок
        buttons.append(InlineKeyboardButton(text=f"{name}", callback_data=f"set_access_level_{level}_{user_id_to_manage}"))
    
    # Розбиваємо кнопки на рядки: тепер по 2
    keyboard = [buttons[i:i + 1] for i in range(0, len(buttons), 1)]
    
    # Кнопка скасування повинна повертати до управління цим же користувачем
    keyboard.append([InlineKeyboardButton(text="Скасувати ❌", callback_data=f"user_{user_id_to_manage}")]) 
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_telethon_actions_keyboard() -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій Telethon."""
    buttons = [
        [InlineKeyboardButton(text="Перевірити статус Telethon 👁️", callback_data="telethon_check_status")],
        [InlineKeyboardButton(text="Авторизувати Telethon 🔑", callback_data="telethon_start_auth")],
        [InlineKeyboardButton(text="Отримати інфо про користувача 🆔", callback_data="telethon_get_user_info")],
        [InlineKeyboardButton(text="Приєднатися до каналу ➕", callback_data="telethon_join_channel")],
        [InlineKeyboardButton(text="⬅️ Назад до адмін-меню", callback_data="cancel_admin_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)