# utils/auth_check.py
import logging
from aiogram import types

logger = logging.getLogger(__name__)

# Цей файл буде розширюватися пізніше
# наприклад, для перевірки прав доступу користувача.

async def is_admin(user_id: int) -> bool:
    """Заглушка: Перевіряє, чи є користувач адміністратором."""
    # Реальна логіка перевірки адміністратора буде тут
    # наприклад, читання з БД або перевірка ADMIN_ID з config.py
    # Поки що, просто повертаємо False або перевіряємо на ADMIN_ID.
    from config import ADMIN_ID
    return user_id == ADMIN_ID

async def check_access(user_id: int) -> bool:
    """Заглушка: Перевіряє, чи має користувач доступ до певного функціоналу."""
    # Реальна логіка перевірки доступу буде тут
    # наприклад, зчитування access_level з БД
    return True # Поки що, усі мають доступ