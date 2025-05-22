# utils/auth_check.py
from database.users_db import get_user_data, add_new_user, update_user_activity # ВИПРАВЛЕНО: update_user_last_activity на update_user_activity
from utils.logger import logger
import asyncio

module_logger = logger.getChild(__name__)

async def handle_user_on_start(user_id: int, username: str, first_name: str, last_name: str) -> dict | None:
    """
    Обробляє користувача при команді /start:
    - Перевіряє, чи існує користувач у БД.
    - Якщо ні, додає його з початковим рівнем доступу.
    - Якщо так, оновлює його дані та час останньої активності.
    - Повертає словник з даними користувача з БД.
    """
    module_logger.info(f"Викликано handle_user_on_start для користувача ID: {user_id}.")
    module_logger.debug(f"Перевіряємо існування користувача ID: {user_id} у БД.")
    
    # Використовуємо функцію get_user_data з database.users_db
    user_data = await get_user_data(user_id) 

    # ДОДАНО ЛОГУВАННЯ ДЛЯ ДІАГНОСТИКИ access_level
    module_logger.debug(f"У handle_user_on_start: Отримані user_data після get_user_data: {user_data}")

    if user_data:
        module_logger.debug(f"Користувач ID: {user_id} знайдений в БД.")
        
        # ДОДАНО ЛОГУВАННЯ ДЛЯ ДІАГНОСТИКИ is_authorized
        module_logger.debug(f"У handle_user_on_start: is_authorized для {user_id}: {user_data.get('is_authorized')}")

        if not user_data.get('is_authorized'):
            module_logger.info(f"Користувач ID: {user_id} не авторизований. Повертаю None.")
            return None
        
        module_logger.info(f"Користувач ID: {user_id} вже існує в БД, спроба оновити активність.")
        # ВИПРАВЛЕНО: Викликаємо update_user_activity тільки з user_id
        await update_user_activity(user_id) 
        module_logger.debug(f"Оновлено час останньої активності для користувача ID: {user_id} при /start.")
        
        # ДОДАНО ЛОГУВАННЯ ПЕРЕД ПОВЕРНЕННЯМ
        module_logger.debug(f"У handle_user_on_start: Повертаю user_data: {user_data}")
        return user_data # Повертаємо дані користувача з БД
    else:
        module_logger.info(f"Новий користувач ID: {user_id}. Додаємо до БД.")
        # Використовуємо функцію add_new_user з database.users_db
        await add_new_user(user_id, username, first_name, last_name)
        module_logger.debug(f"Додано нового користувача ID: {user_id} до БД.")
        
        # Після додавання нового користувача, отримуємо його дані з БД, щоб повернути
        # Це потрібно, щоб отримати повний словник з усіма полями, включаючи access_level
        new_user_data = await get_user_data(user_id)
        # ДОДАНО ЛОГУВАННЯ ПЕРЕД ПОВЕРНЕННЯМ
        module_logger.debug(f"У handle_user_on_start: Повертаю new_user_data: {new_user_data}")
        return new_user_data # Повертаємо дані нового користувача