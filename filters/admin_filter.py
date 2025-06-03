# filters/admin_filter.py
import asyncpg
from aiogram.filters import Filter
from aiogram.types import Message
from typing import Any, Dict, Union

from database.users_db import get_user_access_level # Переконайтеся, що цей імпорт коректний

class AdminAccessFilter(Filter):
    def __init__(self, min_access_level: int = 10):
        self.min_access_level = min_access_level

    async def __call__(self, obj: Union[Message], **data: Any) -> bool:
        # Перевіряємо, чи це повідомлення або CallbackQuery
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, dict) and 'from_user' in obj: # Для випадку, якщо Filter використовується з Callbacks
            user_id = obj['from_user'].id
        else:
            # Це може бути CallbackQuery або інший тип, спробуємо отримати user_id
            user_id = obj.from_user.id # Очікуємо, що from_user завжди є

        # db_pool має бути доступний у `data` завдяки MIDDLEWARE або `dp.workflow_data`
        # Якщо ви ще не налаштували middleware, який передає db_pool,
        # то цей фільтр краще використовувати в хендлерах, де db_pool вже доступний.
        # Або ж, ми можемо передати db_pool через main.py:
        db_pool: asyncpg.Pool = data.get("db_pool")
        
        if not db_pool:
            # Це важлива проблема, якщо db_pool недоступний, логуємо і повертаємо False
            # Або ж переконайтеся, що db_pool передається в dispatcher.workflow_data
            # і доступний через bot.get("db_pool")
            return False 
        
        access_level = await get_user_access_level(db_pool, user_id)
        return access_level >= self.min_access_level

# Створюємо екземпляр фільтра для зручності
is_admin = AdminAccessFilter(min_access_level=10) # Адміністратор - це рівень 10 і вище