# keyboards/callback_factories.py

from aiogram.filters.callback_data import CallbackData
from typing import Optional

class AdminCallback(CallbackData, prefix="admin"):
    action: str
    user_id: Optional[int] = None
    page: Optional[int] = 0
    level: Optional[int] = None

class UserActionCallback(CallbackData, prefix="user_action"):
    action: str
    user_id: int

class AccessLevelCallback(CallbackData, prefix="access_level"):
    level: int
    user_id: int