# handlers/reply_keyboard_handler.py
from aiogram import Router, F
from aiogram.types import Message
from utils.logger import logger
# Імпортуємо функції з users_db
from database.users_db import get_user_data, update_user_activity # ВИПРАВЛЕНО: update_user_last_activity на update_user_activity
# Імпортуємо функції клавіатур
from keyboards.reply_keyboard import create_paginated_keyboard, get_total_pages # Тепер імпортуємо і get_total_pages

router = Router(name="Пагінована клавіатура")
module_logger = logger.getChild(__name__)

# Словник для зберігання поточної сторінки для кожного користувача
# Нагадування: для продакшн-бота краще використовувати FSMContext або базу даних/кеш.
user_pages = {}

# Обробник кнопки "➡️ Іще"
@router.message(F.text == "➡️ Іще")
async def next_page_command(message: Message):
    user_id = message.from_user.id
    # username = message.from_user.username # НЕ ПОТРІБНО для update_user_activity
    # first_name = message.from_user.first_name # НЕ ПОТРІБНО для update_user_activity
    # last_name = message.from_user.last_name # НЕ ПОТРІБНО для update_user_activity

    user_db_data = await get_user_data(user_id)
    # Оновлюємо час останньої активності користувача при натисканні кнопки
    await update_user_activity(user_id) # ВИПРАВЛЕНО: Тепер тільки user_id

    access_level = user_db_data.get("access_level", 0) if user_db_data else 0

    current_page = user_pages.get(user_id, 1)
    
    total_pages = get_total_pages(access_level) # Отримуємо загальну кількість сторінок
    
    if current_page < total_pages:
        next_page = current_page + 1
        user_pages[user_id] = next_page
        module_logger.info(f"Користувач {user_id} перейшов на сторінку {next_page} (Рівень доступу: {access_level}).")
        
        # Передаємо user_access_level замість access_level, як це очікує create_paginated_keyboard
        new_keyboard = create_paginated_keyboard(page=next_page, user_access_level=access_level)
        await message.answer("Наступна сторінка:", reply_markup=new_keyboard)
    else:
        module_logger.warning(f"Користувач {user_id} спробував перейти на сторінку {current_page + 1}, але це вже остання сторінка ({total_pages}).")
        # Відправляємо поточну сторінку, якщо вже на останній
        await message.answer("Це остання доступна сторінка.", 
                             reply_markup=create_paginated_keyboard(page=current_page, user_access_level=access_level)) 

# Обробник кнопки "⬅️ Назад"
@router.message(F.text == "⬅️ Назад")
async def prev_page_command(message: Message):
    user_id = message.from_user.id
    # username = message.from_user.username # НЕ ПОТРІБНО
    # first_name = message.from_user.first_name # НЕ ПОТРІБНО
    # last_name = message.from_user.last_name # НЕ ПОТРІБНО

    user_db_data = await get_user_data(user_id)
    await update_user_activity(user_id) # ВИПРАВЛЕНО: Тепер тільки user_id

    access_level = user_db_data.get("access_level", 0) if user_db_data else 0

    current_page = user_pages.get(user_id, 1)
    
    if current_page > 1:
        prev_page = current_page - 1
        user_pages[user_id] = prev_page
        module_logger.info(f"Користувач {user_id} повернувся на сторінку {prev_page} (Рівень доступу: {access_level}).")
        await message.answer("Попередня сторінка:", 
                             reply_markup=create_paginated_keyboard(page=prev_page, user_access_level=access_level))
    else:
        module_logger.warning(f"Користувач {user_id} спробував перейти на сторінку {current_page - 1}, але це вже перша сторінка.")
        await message.answer("Це перша сторінка.", 
                             reply_markup=create_paginated_keyboard(page=current_page, user_access_level=access_level))

# Обробник кнопки "🏡 Головна"
@router.message(F.text == "🏡 Головна")
async def main_menu_command(message: Message):
    user_id = message.from_user.id
    # username = message.from_user.username # НЕ ПОТРІБНО
    # first_name = message.from_user.first_name # НЕ ПОТРІБНО
    # last_name = message.from_user.last_name # НЕ ПОТРІБНО

    user_db_data = await get_user_data(user_id)
    await update_user_activity(user_id) # ВИПРАВЛЕНО: Тепер тільки user_id

    access_level = user_db_data.get("access_level", 0) if user_db_data else 0

    user_pages[user_id] = 1 # Скидаємо сторінку на першу
    module_logger.info(f"Користувач {user_id} повернувся до головного меню (стор. 1, Рівень доступу: {access_level}).")
    await message.answer("Повернення до головного меню:", 
                         reply_markup=create_paginated_keyboard(page=1, user_access_level=access_level))