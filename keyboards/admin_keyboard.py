# keyboards/admin_keyboard.py
import math
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.constants import ACCESS_LEVEL_BUTTONS
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback, ChatListCallback, ChatInfoCallback

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Повертає головну клавіатуру адміністратора з оновленими кнопками."""
    # Використовуємо InlineKeyboardBuilder для консистентності
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👥 Юзер-матриця · Редактор доступу",
        callback_data=AdminCallback(action="show_users").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="🔐 TeleKey · Авторизація API-зв’язку",
        callback_data=AdminCallback(action="telethon_auth").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="💬 Чат-матриця · Перегляд активних зон",
        callback_data=AdminCallback(action="chat_matrix").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="🏁 Завершити командування",
        callback_data=AdminCallback(action="close_admin_panel").pack()
    ))
    return builder.as_markup()

def get_users_list_keyboard(users: list, current_page: int, users_per_page: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру зі списком користувачів для вибору та пагінації."""
    builder = InlineKeyboardBuilder()

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
            builder.row(InlineKeyboardButton(
                text=button_text,
                callback_data=AdminCallback(action="select_user", user_id=user_id).pack()
            ))

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
            callback_data="users_current_page_info" # Цю кнопку не потрібно обробляти як CallbackData
        )
    )
    if current_page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=AdminCallback(action="show_users", page=current_page + 1).pack()
            )
        )
    if pagination_buttons: # Додаємо рядок з пагінацією, тільки якщо є кнопки
        builder.row(*pagination_buttons)
        
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до адмін-меню",
            callback_data=AdminCallback(action="cancel_admin_action").pack()
        )
    )
    return builder.as_markup()

def get_user_actions_keyboard(is_authorized: bool, current_access_level: int, user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій з конкретним користувачем."""
    builder = InlineKeyboardBuilder()
    if is_authorized:
        builder.row(InlineKeyboardButton(
            text="Деавторизувати ❌",
            callback_data=UserActionCallback(action="unauthorize", target_user_id=user_id_to_manage).pack()
        ))
    else:
        builder.row(InlineKeyboardButton(
            text="Авторизувати ✅",
            callback_data=UserActionCallback(action="authorize", target_user_id=user_id_to_manage).pack()
        ))
    builder.row(InlineKeyboardButton(
        text=f"Змінити рівень доступу ({current_access_level}) ⬆️",
        callback_data=AdminCallback(action="change_access_level", user_id=user_id_to_manage).pack()
    ))
    # Кнопка назад до списку користувачів
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад до списку користувачів",
        callback_data=AdminCallback(action="show_users").pack()
    ))
    # Кнопка назад до адмін-меню
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад до адмін-меню",
        callback_data=AdminCallback(action="cancel_admin_action").pack()
    ))
    return builder.as_markup()

def get_confirm_action_keyboard(action: str, user_id: int, level: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Повертає клавіатуру підтвердження дії.
    action: тип дії (наприклад, "authorize", "unauthorize", "set_level")
    user_id: ID користувача, якого стосується дія
    level: новий рівень доступу, якщо дія "set_level"
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Підтвердити ✅",
        callback_data=UserActionCallback(action=f"confirm_{action}", target_user_id=user_id, level=level).pack()
    ))
    # Змінено: повернення до меню дій з користувачем, а не просто скасування адмін-дії
    builder.row(InlineKeyboardButton(
        text="Скасувати ❌",
        callback_data=AdminCallback(action="select_user", user_id=user_id).pack() # Повертаємось до меню конкретного користувача
    ))
    return builder.as_markup()

def get_access_level_keyboard(user_id_to_manage: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з кнопками для вибору рівня доступу."""
    builder = InlineKeyboardBuilder()
    for level, name in ACCESS_LEVEL_BUTTONS:
        builder.button(
            text=f"{name}",
            callback_data=AccessLevelCallback(action="set_level", level=level, target_user_id=user_id_to_manage).pack()
        )
    builder.adjust(1) # Розміщуємо по 1 кнопці в рядку для кращої читабельності
    builder.row(
        InlineKeyboardButton(
            text="Скасувати ❌",
            callback_data=AdminCallback(action="select_user", user_id=user_id_to_manage).pack()
        )
    )
    return builder.as_markup()

def get_telethon_actions_keyboard() -> InlineKeyboardMarkup:
    """Повертає клавіатуру для дій Telethon (БЕЗ авторизації, приєднання до каналу та видалення сесії)."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Перевірити статус Telethon 👁️",
        callback_data=AdminCallback(action="telethon_check_status").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="Отримати інфо про користувача 🆔",
        callback_data=AdminCallback(action="telethon_get_user_info").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад до адмін-меню",
        callback_data=AdminCallback(action="cancel_admin_action").pack()
    ))
    return builder.as_markup()

def get_telethon_code_retry_keyboard() -> InlineKeyboardMarkup:
    """
    Повертає інлайн-клавіатуру для повторного введення або запиту нового коду
    в процесі авторизації Telethon.
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔄 Запитати новий код",
        callback_data=AdminCallback(action="telethon_resend_code").pack()
    ))
    builder.row(InlineKeyboardButton(
        text="❌ Скасувати авторизацію",
        callback_data=AdminCallback(action="telethon_cancel_auth").pack()
    ))
    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Повертає інлайн-клавіатуру з однією кнопкою 'Скасувати', призначена для адмін-меню."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="❌ Скасувати",
        callback_data=AdminCallback(action="cancel_admin_action").pack()
    ))
    return builder.as_markup()

def get_chat_matrix_keyboard() -> InlineKeyboardMarkup:
    """
    Повертає інлайн-клавіатуру для управління чат-матрицею.
    """
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
            text="🔙 Назад до адмін-меню",
            callback_data=AdminCallback(action="cancel_admin_action").pack()
        )
    )
    return builder.as_markup()

# Додаємо функцію для кнопки "Назад до Чат-матриці" (винесено з handler'ів)
def get_back_to_chat_matrix_keyboard() -> InlineKeyboardMarkup:
    """
    Повертає клавіатуру з кнопкою "⬅️ Назад до Чат-матриці".
    Використовується для повернення з різних підменю Чат-матриці.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до Чат-матриці",
            callback_data=AdminCallback(action="chat_matrix").pack()
        )
    )
    return builder.as_markup()


# -----------------------------------------------------------
# НОВІ КЛАВІАТУРИ ДЛЯ ЧАТ-МАТРИЦІ
# -----------------------------------------------------------

def get_search_results_keyboard(chats: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for chat in chats:
        status_emoji = "✅" if chat['is_added'] else "➕"
        button_text = f"{status_emoji} {chat['chat_title']}"
        builder.row(InlineKeyboardButton(
            text=button_text,
            callback_data=ChatListCallback(action="view_chat_details", chat_id=chat['chat_id'], from_search=True).pack() # Додаємо from_search=True
        ))
    
    # Кнопка повернення до головного меню Чат-матриці
    builder.row(InlineKeyboardButton(
        text="🔙 В головне меню Чат-матриці",
        callback_data=AdminCallback(action="chat_matrix").pack()
    ))
    return builder.as_markup()

def get_allowed_chats_list_keyboard(allowed_chats: list, current_page: int, chats_per_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_chats = len(allowed_chats)
    start_index = current_page * chats_per_page
    end_index = min(start_index + chats_per_page, total_chats)
    
    chats_on_page = allowed_chats[start_index:end_index]

    # Видалено логіку, яка скидала current_page на 0, це має керуватися хендлером.
    # Якщо чатів на сторінці немає, це означає, що ми не повинні були туди потрапити або список порожній.

    for chat in chats_on_page:
        builder.row(InlineKeyboardButton(
            text=chat['chat_title'],
            callback_data=ChatListCallback(action="view_chat_details", chat_id=chat['chat_id'], page=current_page, from_search=False).pack() # Додаємо from_search=False
        ))

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Попередня", callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page - 1).pack())
        )
    # Кнопка з поточною сторінкою (якщо потрібно)
    if total_chats > 0: # Показуємо номер сторінки, тільки якщо є чати
        total_pages = math.ceil(total_chats / chats_per_page)
        navigation_buttons.append(
            InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="current_page_info_allowed")
        )

    if end_index < total_chats:
        navigation_buttons.append(
            InlineKeyboardButton(text="Наступна ➡️", callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page + 1).pack())
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)

    builder.row(InlineKeyboardButton(
        text="🔙 Назад до меню Чат-матриці", # Більш конкретна назва
        callback_data=AdminCallback(action="chat_matrix").pack()
    ))

    return builder.as_markup()

def get_chat_info_keyboard(chat_id: int, is_added: bool, current_page: int, is_search_context: bool = False) -> InlineKeyboardMarkup:
    """
    Клавіатура для деталей чату, з опціями додавання/видалення.
    is_search_context: True, якщо ми прийшли сюди з пошуку, False, якщо зі списку дозволених.
    """
    builder = InlineKeyboardBuilder()
    if not is_added:
        builder.row(InlineKeyboardButton(text="Додати до дозволених",
                                         callback_data=ChatInfoCallback(action="add_allowed_chat_from_details", chat_id=chat_id, page=current_page, from_search=is_search_context).pack()))
    else:
        builder.row(InlineKeyboardButton(text="🗑️ Видалити чат",
                                         callback_data=ChatInfoCallback(action="delete_allowed_chat", chat_id=chat_id, page=current_page, from_search=is_search_context).pack()))
    
    if is_search_context:
        # Повертаємось до попереднього стану пошуку (якщо необхідно), або до загального меню Чат-матриці
        # Якщо ми хочемо повернутися до результатів пошуку, то треба передавати поточний пошуковий запит
        # Але поки що повертаємось до старту пошуку
        builder.row(InlineKeyboardButton(text="🔙 В головне меню Чат-матриці", # Змінено на повернення до загального меню Чат-матриці
                                         callback_data=AdminCallback(action="chat_matrix").pack()))
    else:
        builder.row(InlineKeyboardButton(text="🔙 Повернутися до списку чатів", # Більш конкретна назва
                                         callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page).pack()))
    
    return builder.as_markup()

def get_confirm_delete_chat_keyboard(chat_id: int, current_page: int, from_search: bool = False) -> InlineKeyboardMarkup:
    """
    Клавіатура підтвердження видалення чату.
    from_search: True, якщо видаляємо з контексту пошуку.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити видалення",
                             callback_data=ChatInfoCallback(action="confirm_delete_allowed_chat", chat_id=chat_id, page=current_page, from_search=from_search).pack())
    )
    builder.row(
        InlineKeyboardButton(text="❌ Скасувати",
                             callback_data=ChatInfoCallback(action="back_to_chat_info", chat_id=chat_id, page=current_page, from_search=from_search).pack())
    )
    return builder.as_markup()