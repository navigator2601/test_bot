from aiogram.filters.callback_data import CallbackData
from typing import Optional

# --- CallbackData для адміністративної панелі ---
class AdminCallback(CallbackData, prefix="admin"):
    """
    CallbackData для загальних адміністративних дій.
    Може включати додаткові поля для передачі контексту між етапами адмін-панелі,
    такими як керування користувачами або додавання чатів.
    """
    action: str  # Дія, наприклад: "admin_chat_matrix_menu", "add_chat_to_allowed", "delete_user"
    
    # Поля, необхідні для передачі даних про чат при додаванні/видаленні через адмін-панель
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    chat_type: Optional[str] = None
    chat_username: Optional[str] = None

    # Поля для керування користувачами
    user_id: Optional[int] = None
    access_level: Optional[int] = None

    # Поля для пагінації (якщо AdminsCallback також використовуватиметься для пагінації)
    page: Optional[int] = None


# --- CallbackData для дій з конкретним користувачем ---
class UserActionCallback(CallbackData, prefix="user_action"):
    """
    CallbackData для дій, що стосуються конкретного користувача (наприклад, бан, розбан).
    """
    action: str  # Дія, наприклад: "ban", "unban", "view_details"
    target_user_id: int # ID користувача, над яким виконується дія


# --- CallbackData для зміни рівня доступу користувача ---
class AccessLevelCallback(CallbackData, prefix="access_level"):
    """
    CallbackData для зміни рівня доступу користувача.
    """
    action: str  # Дія, наприклад: "set"
    target_user_id: int # ID користувача, якому змінюється рівень
    level: int # Новий рівень доступу


# --- CallbackData для керування списком чатів (результати пошуку, пагінація) ---
class ChatListCallback(CallbackData, prefix="chat_list"):
    """
    CallbackData для кнопок у списку чатів (результати пошуку, пагінація та вибір чату).
    Використовується для переходу від списку до деталей чату.
    """
    action: str  # 'view_chat_details' (для перегляду деталей чату), 'paginate' (для пагінації)
    chat_id: Optional[int] = None # ID чату, якщо action='view_chat_details'
    page: Optional[int] = None # Номер сторінки, якщо action='paginate'


# --- CallbackData для детальної інформації про чат та дій над ним ---
class ChatInfoCallback(CallbackData, prefix="chat_info"):
    """
    CallbackData для дій на сторінці інформації про чат.
    Використовується для виконання конкретних дій з вибраним чатом (наприклад, приєднатися, покинути, видалити).
    """
    action: str # 'add_member', 'delete_chat', 'back_to_list', 'confirm_delete_chat'
    chat_id: int # ID чату, з яким виконується дія
    page: Optional[int] = None # Для повернення на правильну сторінку списку чатів (якщо потрібно)