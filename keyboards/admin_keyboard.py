from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import Optional # Імпорт Optional для типізації

from keyboards.callback_factories import (
    AdminCallback,
    ChatListCallback,
    ChatInfoCallback
    # Додайте інші CallbackFactory, якщо вони потрібні для user_actions або загальних підтверджень
    # UserCallback # Наприклад, якщо у вас є окремий колбек для користувачів
    # ConfirmActionCallback # Якщо ви створюєте окремий колбек для підтверджень
)

# -----------------------------------------------------------
# Main Admin Keyboard
# -----------------------------------------------------------

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="👤 Управління користувачами",
            callback_data=AdminCallback(action="manage_users").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="💬 Чат-матриця · Перегляд активних зон",
            callback_data=AdminCallback(action="chat_matrix").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🤖 Керування сесіями Telethon",
            callback_data=AdminCallback(action="manage_telethon_sessions").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📊 Статистика",
            callback_data=AdminCallback(action="view_stats").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до головного меню",
            callback_data=AdminCallback(action="back_to_main_menu").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Chat Matrix Keyboard
# -----------------------------------------------------------

def get_chat_matrix_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📜 Список підключених чатів",
            callback_data=AdminCallback(action="view_allowed_chats").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔍 Пошук чатів",
            callback_data=AdminCallback(action="search_chats_admin").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="back_to_admin_main_menu_from_chat_matrix").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Search Results Keyboard
# -----------------------------------------------------------

def get_search_results_keyboard(chats: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for chat in chats:
        status_emoji = "✅" if chat['is_added'] else "➕"
        button_text = f"{status_emoji} {chat['chat_title']}"
        # При натисканні на кнопку переходимо до деталей чату
        builder.row(InlineKeyboardButton(
            text=button_text,
            callback_data=ChatListCallback(action="view_chat_details", chat_id=chat['chat_id']).pack()
        ))
    
    # Кнопка повернення до пошуку
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад до пошуку",
        callback_data=AdminCallback(action="search_chats_admin").pack() # Повертаємось до початкового запиту пошуку
    ))
    # Кнопка повернення до головного меню Чат-матриці
    builder.row(InlineKeyboardButton(
        text="🔙 В головне меню Чат-матриці",
        callback_data=AdminCallback(action="chat_matrix_menu").pack()
    ))
    return builder.as_markup()

# -----------------------------------------------------------
# Allowed Chats List Keyboard
# -----------------------------------------------------------

def get_allowed_chats_list_keyboard(allowed_chats: list, current_page: int, chats_per_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_chats = len(allowed_chats)
    start_index = current_page * chats_per_page
    end_index = min(start_index + chats_per_page, total_chats)
    
    chats_on_page = allowed_chats[start_index:end_index]

    # Якщо на поточній сторінці немає чатів, але це не перша, повертаємося на першу
    if not chats_on_page and current_page > 0 and total_chats > 0:
        current_page = 0 
        start_index = 0
        end_index = min(chats_per_page, total_chats)
        chats_on_page = allowed_chats[start_index:end_index]


    for chat in chats_on_page:
        # Створюємо кнопку для кожного чату
        builder.row(InlineKeyboardButton(
            text=chat['chat_title'],
            callback_data=ChatListCallback(action="view_chat_details", chat_id=chat['chat_id'], page=current_page).pack()
        ))

    # Додаємо кнопки пагінації
    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Попередня", callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page - 1).pack())
        )
    if end_index < total_chats:
        navigation_buttons.append(
            InlineKeyboardButton(text="Наступна ➡️", callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page + 1).pack())
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)

    # Кнопка "Назад до меню Чат-матриці"
    builder.row(InlineKeyboardButton(
        text="🔙 Назад до меню",
        callback_data=AdminCallback(action="chat_matrix_menu").pack() # Використовуємо AdminCallback для повернення
    ))

    return builder.as_markup()

# -----------------------------------------------------------
# Chat Info Keyboard (For details, add/remove)
# -----------------------------------------------------------

def get_chat_info_keyboard(chat_id: int, is_added: bool, current_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not is_added:
        builder.row(InlineKeyboardButton(text="Додати до дозволених",
                                         callback_data=ChatInfoCallback(action="add_allowed_chat_from_details", chat_id=chat_id, page=current_page).pack()))
    else:
        builder.row(InlineKeyboardButton(text="🗑️ Видалити чат",
                                         callback_data=ChatInfoCallback(action="delete_allowed_chat", chat_id=chat_id, page=current_page).pack()))
    
    builder.row(InlineKeyboardButton(text="🔙 Повернутися до списку",
                                     callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page).pack()))
    
    return builder.as_markup()


# -----------------------------------------------------------
# Confirmation Keyboard for Deletion
# -----------------------------------------------------------

def get_confirm_delete_chat_keyboard(chat_id: int, current_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити видалення",
                             callback_data=ChatInfoCallback(action="confirm_delete_allowed_chat", chat_id=chat_id, page=current_page).pack())
    )
    builder.row(
        InlineKeyboardButton(text="❌ Скасувати",
                             callback_data=ChatInfoCallback(action="back_to_chat_info", chat_id=chat_id, page=current_page).pack())
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Users List Keyboard (Placeholder for 'manage_users' section)
# -----------------------------------------------------------

def get_users_list_keyboard() -> InlineKeyboardMarkup:
    """
    Клавіатура для меню "Управління користувачами".
    Ця функція є заглушкою і має бути розширена для відображення списку користувачів
    та надання функцій їх адміністрування (наприклад, додати/видалити адміна).
    """
    builder = InlineKeyboardBuilder()
    # Приклад: Кнопка "Додати нового користувача", якщо це доречно
    # builder.row(InlineKeyboardButton(text="➕ Додати користувача", callback_data=AdminCallback(action="add_user").pack()))
    # builder.row(InlineKeyboardButton(text="Список користувачів", callback_data=AdminCallback(action="view_users").pack()))

    # Обов'язкова кнопка для повернення
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="back_to_admin_main_menu").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# User Actions Keyboard (Placeholder for 'get_user_actions_keyboard')
# -----------------------------------------------------------

def get_user_actions_keyboard(user_id: int, is_admin: bool) -> InlineKeyboardMarkup:
    """
    Клавіатура для дій над конкретним користувачем.
    Ця функція є заглушкою і має бути розширена для реальних дій,
    таких як "Зробити адміном", "Видалити адміна", "Заблокувати користувача" тощо.
    """
    builder = InlineKeyboardBuilder()

    # Приклад кнопки, яку ви б використовували:
    # if is_admin:
    #     builder.row(InlineKeyboardButton(text="Зняти права адміна", callback_data=AdminCallback(action=f"remove_admin_{user_id}").pack()))
    # else:
    #     builder.row(InlineKeyboardButton(text="Призначити адміном", callback_data=AdminCallback(action=f"make_admin_{user_id}").pack()))

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до списку користувачів",
            callback_data=AdminCallback(action="manage_users").pack() # Повернення до списку користувачів
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад до адмін-меню",
            callback_data=AdminCallback(action="back_to_admin_main_menu").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# General Confirmation Keyboard (Placeholder for 'get_confirm_action_keyboard')
# -----------------------------------------------------------

def get_confirm_action_keyboard(callback_data_on_confirm: str, callback_data_on_cancel: str, message_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Універсальна клавіатура для підтвердження дії.
    Приймає callback_data для кнопки "Так" і "Ні".
    Може також приймати message_id, якщо потрібно передати його далі.
    """
    builder = InlineKeyboardBuilder()
    
    confirm_data_packed = callback_data_on_confirm
    cancel_data_packed = callback_data_on_cancel

    # Якщо у вас є ConfirmActionCallback, ви можете використовувати його так:
    # confirm_data_packed = ConfirmActionCallback(action="confirm", original_action=callback_data_on_confirm, message_id=message_id).pack()
    # cancel_data_packed = ConfirmActionCallback(action="cancel", original_action=callback_data_on_cancel, message_id=message_id).pack()


    builder.row(
        InlineKeyboardButton(text="✅ Так, підтвердити", callback_data=confirm_data_packed),
        InlineKeyboardButton(text="❌ Скасувати", callback_data=cancel_data_packed)
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Access Level Keyboard (Placeholder for 'get_access_level_keyboard')
# -----------------------------------------------------------

def get_access_level_keyboard(user_id: int, current_level: str) -> InlineKeyboardMarkup:
    """
    Клавіатура для вибору рівня доступу користувача.
    Це заглушка, яку потрібно буде розширити для реальних рівнів доступу.
    """
    builder = InlineKeyboardBuilder()

    # Приклади кнопок:
    # builder.row(InlineKeyboardButton(text="Звичайний користувач", callback_data=f"set_access_level_{user_id}_user"))
    # builder.row(InlineKeyboardButton(text="Модератор", callback_data=f"set_access_level_{user_id}_moderator"))
    # builder.row(InlineKeyboardButton(text="Адміністратор", callback_data=f"set_access_level_{user_id}_admin"))

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до дій над користувачем",
            callback_data=AdminCallback(action="view_user_details", user_id=user_id).pack() # Повернення до деталей користувача
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад до адмін-меню",
            callback_data=AdminCallback(action="back_to_admin_main_menu").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Telethon Actions Keyboard (New placeholder for 'get_telethon_actions_keyboard')
# -----------------------------------------------------------

def get_telethon_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Клавіатура для керування сесіями Telethon.
    Це заглушка, яку потрібно буде розширити для реальних дій,
    таких як "Додати сесію", "Видалити сесію", "Переглянути статус" тощо.
    """
    builder = InlineKeyboardBuilder()
    
    # Приклади кнопок:
    # builder.row(InlineKeyboardButton(text="➕ Додати сесію", callback_data=AdminCallback(action="add_telethon_session").pack()))
    # builder.row(InlineKeyboardButton(text="🗑️ Видалити сесію", callback_data=AdminCallback(action="delete_telethon_session").pack()))
    # builder.row(InlineKeyboardButton(text="🔄 Переглянути статус сесій", callback_data=AdminCallback(action="view_telethon_sessions_status").pack()))

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="back_to_admin_main_menu").pack()
        )
    )
    return builder.as_markup()

# -----------------------------------------------------------
# Example of a generic back button (can be removed if not used)
# -----------------------------------------------------------
def get_back_button(callback_data_value: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=callback_data_value
        )
    )
    return builder.as_markup()