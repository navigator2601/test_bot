# keyboards/callback_factories.py

from aiogram.filters.callback_data import CallbackData
from typing import Optional

# --- CallbackData для адміністративної панелі ---
class AdminCallback(CallbackData, prefix="admin"):
    """
    CallbackData для загальних адміністративних дій.
    """
    action: str
    
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    chat_type: Optional[str] = None
    chat_username: Optional[str] = None

    user_id: Optional[int] = None
    access_level: Optional[int] = None

    page: Optional[int] = None


# --- CallbackData для дій з конкретним користувачем ---
class UserActionCallback(CallbackData, prefix="user_action"):
    """
    CallbackData для дій, що стосуються конкретного користувача.
    """
    action: str
    target_user_id: int


# --- CallbackData для зміни рівня доступу користувача ---
class AccessLevelCallback(CallbackData, prefix="access_level"):
    """
    CallbackData для зміни рівня доступу користувача.
    """
    action: str
    target_user_id: int
    level: int


# --- CallbackData для керування списком чатів ---
class ChatListCallback(CallbackData, prefix="chat_list"):
    """
    CallbackData для кнопок у списку чатів.
    """
    action: str
    chat_id: Optional[int] = None
    page: Optional[int] = None
    from_search: Optional[bool] = False


# --- CallbackData для детальної інформації про чат та дій над ним ---
class ChatInfoCallback(CallbackData, prefix="chat_info"):
    """
    CallbackData для дій на сторінці інформації про чат.
    """
    action: str
    chat_id: int
    page: Optional[int] = None
    from_search: Optional[bool] = False


# --- CallbackData для каталогу кондиціонерів ---
class CatalogCallback(CallbackData, prefix="catalog"):
    """
    CallbackData для кнопок каталогу.
    """
    action: str
    brand_id: Optional[int] = None
    model_id: Optional[int] = None
    brand_name: Optional[str] = None