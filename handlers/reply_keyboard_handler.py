import logging
import math
from aiogram import Router, types, Bot, Dispatcher, F 
import asyncpg
from keyboards.reply_keyboard import get_main_menu_keyboard, BUTTONS_PER_PAGE, BUTTONS_CONFIG
from keyboards.admin_keyboard import get_admin_main_keyboard
from database.users_db import get_user_access_level
import random # <--- ДОДАНО ЦЕЙ ІМПОРТ

logger = logging.getLogger(__name__)
router = Router()
user_menu_page = {}

ADMIN_WELCOME_MESSAGES = [
    "<b>⚙️ Refridex OS:</b>\n “Сигнал підтверджено. Відкриваю панель командування ядром.”",
    "<b>💻 Refridex OS:</b>\n “Адмін-доступ авторизовано. Обери свій шлях, Контролере.”",
    "<b>🔐 Refridex OS:</b>\n “Ти пройшов крізь ідентифікацію. Панель адміністратора активна.”",
    "<b>🧊 Refridex OS:</b>\n “Привіт, Хранителю системи. Параметри під контролем.”",
    "<b>📡 Refridex OS:</b>\n “Підключення до внутрішнього інтерфейсу встановлено. Команди доступні.”",
    "<b>🪞 Refridex OS:</b>\n “Панель керування розблокована. Твоя воля — мій протокол.”",
    "<b>🧬 Refridex OS:</b>\n “Ти в центрі управління. Система слухає.”",
    "<b>🧠 Refridex OS:</b>\n “Адмін-інтерфейс запущено. Дії очікуються...”",
    "<b>💿 Refridex OS:</b>\n “Контрольна консоль активна. Вибери операцію, Модераторе.”",
    "<b>⚡ Refridex OS:</b>\n “Нульовий доступ обійдено. Панель відкрито через альтернативний порт.”",
    "<b>🧯 Refridex OS:</b>\n “Адміністратор з'явився. Відкриваю можливості управління.”",
    "<b>📟 Refridex OS:</b>\n “Доступ до панелі отримано. Зчитування привілеїв...”",
    "<b>🔧 Refridex OS:</b>\n “Серце системи відкрито. Виконуй свій протокол.”",
    "<b>🧭 Refridex OS:</b>\n “Ти — в командному центрі. Визнач свою ціль.”",
    "<b>🔊 Refridex OS:</b>\n “Я слухаю, Керівнику. Обирай наступну дію.”"
]
# ---------------------------------------------------

def get_access_level_description(access_level: int) -> tuple[str, str]:
    if access_level == 0:
        return "🌐 Гість Системи", "Має мінімальний доступ до базових функцій."
    elif 1 <= access_level <= 2:
        return "🎮 Пілот Блоку", "Може управляти деякими режимами та викликати діагностику."
    elif 3 <= access_level <= 5:
        return "🔧 Інженер Зони", "Має доступ до звітності, розширених налаштувань."
    elif 6 <= access_level <= 9:
        return "🧠 Техно-Оператор HVAC", "Знає, що таке субохолодження. Аналізує дані та зберігає баланс."
    elif access_level >= 10:
        return "🧬 Адміністратор Ядра", "Має ключ до всіх баз. Може перепрошити саму суть Рефрідекса."
    else:
        return "❓ Невідомий рівень доступу", "Зверніться до адміністратора."

@router.message(F.text == "⬅️ Назад")
@router.message(F.text == "➡️ Іще")
async def show_main_menu(message: types.Message, dispatcher: Dispatcher) -> None:
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    is_pagination_action = message.text in ["⬅️ Назад", "➡️ Іще"]
    logger.info(f"Користувач {user_name} (ID: {user_id}) запитав меню або натиснув пагінацію.")
    
    if not db_pool:
        logger.error("db_pool_instance не знайдено в dispatcher.workflow_data для show_main_menu!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id) 
    if access_level is None:
        access_level = 0
    logger.info(f"Користувач {user_name} (ID: {user_id}) має рівень доступу: {access_level}.")
    
    all_available_buttons_for_user = []
    for level_key in sorted(BUTTONS_CONFIG.keys()):
        if access_level >= level_key:
            for button_text, min_button_level in BUTTONS_CONFIG[level_key]:
                if access_level >= min_button_level and button_text not in [btn[0] for btn in all_available_buttons_for_user]:
                    all_available_buttons_for_user.append((button_text, min_button_level))
    
    current_page = user_menu_page.get(user_id, 0)
    if message.text == "⬅️ Назад":
        current_page = max(0, current_page - 1)
    elif message.text == "➡️ Іще":
        total_buttons = len(all_available_buttons_for_user)
        total_pages = math.ceil(total_buttons / BUTTONS_PER_PAGE) if total_buttons > 0 else 1
        current_page = min(total_pages - 1, current_page + 1)
    
    user_menu_page[user_id] = current_page
    
    buttons_on_current_page_count = len(all_available_buttons_for_user[current_page * BUTTONS_PER_PAGE : (current_page * BUTTONS_PER_PAGE) + BUTTONS_PER_PAGE])
    logger.info(f"Користувачу {user_name} (ID: {user_id}) відображається {buttons_on_current_page_count} кнопок на сторінці {current_page + 1}.")
    
    menu_message_text = ""
    if is_pagination_action:
        if message.text == "⬅️ Назад":
            menu_message_text = "Ви повернулись до попередньої клавіатури."
        elif message.text == "➡️ Іще":
            menu_message_text = "Ви перейшли до наступної клавіатури."
    else:
        level_name, level_description = get_access_level_description(access_level)
        menu_message_text = (
            "Ваш рівень доступу:\n"
            f"<b>{level_name}</b>\n"
            f"{level_description}"
        )
            
    keyboard = await get_main_menu_keyboard(access_level, current_page)
    await message.answer(menu_message_text, reply_markup=keyboard, parse_mode='HTML')


# НОВИЙ ХЕНДЛЕР ДЛЯ КНОПКИ "⚙️ АДМІНІСТРУВАННЯ"
@router.message(F.text == "⚙️ Адміністрування")
async def handle_admin_button(message: types.Message, dispatcher: Dispatcher) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    db_pool = dispatcher.workflow_data.get('db_pool_instance')

    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку '⚙️ Адміністрування'.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в dispatcher.workflow_data для handle_admin_button!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0 
    
    # Перевірка, чи має користувач рівень доступу 10 або вище для адмін-панелі
    if access_level >= 10: 
        admin_keyboard = get_admin_main_keyboard() # Отримуємо клавіатуру адмін-панелі
        
        # --- ЗМІНЕНО: Вибираємо випадкове повідомлення та формуємо текст ---
        welcome_admin_text = random.choice(ADMIN_WELCOME_MESSAGES)
        await message.answer(
            f"{welcome_admin_text}", 
            reply_markup=admin_keyboard, 
            parse_mode='HTML'
        )
        # --- КІНЕЦЬ ЗМІН ---
        logger.info(f"Користувачу {user_id} (рівень {access_level}) відображено панель адміністратора.")
    else:
        # Якщо у користувача немає доступу, повертаємо його до головного меню
        await message.answer(
            "У вас немає доступу до панелі адміністратора.", 
            reply_markup=await get_main_menu_keyboard(access_level, user_menu_page.get(user_id, 0)) # Повертаємо поточну сторінку меню
        )
        logger.warning(f"Користувач {user_id} (рівень {access_level}) спробував отримати доступ до адмін-панелі без дозволу.")