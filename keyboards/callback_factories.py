from aiogram.filters.callback_data import CallbackData
from typing import Optional

class AdminCallback(CallbackData, prefix="admin"):
    action: str
    page: Optional[int] = None
    user_id: Optional[int] = None
    access_level: Optional[int] = None
    
    # ОНОВЛЕНІ ПОЛЯ: Для передачі інформації про чат, включаючи тип та юзернейм
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    chat_type: Optional[str] = None  # НОВЕ ПОЛЕ
    username: Optional[str] = None   # НОВЕ ПОЛЕ

class UserActionCallback(CallbackData, prefix="user_action"):
    action: str
    target_user_id: int

class AccessLevelCallback(CallbackData, prefix="access_level"):
    action: str
    target_user_id: int
    level: int