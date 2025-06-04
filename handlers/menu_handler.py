# handlers/menu_handler.py
import logging
import math # Все ще потрібен, якщо використовується math.ceil напряму (але тепер буде викликатися з keyboards.reply_keyboard)

from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode # <--- ДОДАНО ЦЕЙ ІМПОРТ
import asyncpg

from keyboards.reply_keyboard import get_main_menu_keyboard, get_main_menu_pages_info # <--- ОНОВЛЕНО ІМПОРТИ
from keyboards.admin_keyboard import get_admin_main_keyboard
from database.users_db import get_user_access_level
from common.messages import get_access_level_description, get_random_admin_welcome_message # <--- ОНОВЛЕНО ІМПОРТИ
from common.constants import BUTTONS_PER_PAGE, ALL_MENU_BUTTONS # <--- ОНОВЛЕНО ІМПОРТИ

logger = logging.getLogger(__name__)

router = Router()

# СТАНИ FSM ДЛЯ МЕНЮ
class MenuStates(StatesGroup):
    main_menu = State() # Стан, коли користувач знаходиться в головному меню
    admin_panel = State() # Стан для адмін-панелі

# ГЛОБАЛЬНА ЗМІННА user_menu_page БІЛЬШЕ НЕ ПОТРІБНА!
# user_menu_page = {} # <--- ЦЕЙ РЯДОК МАЄ БУТИ ВИДАЛЕНО!

# ADMIN_WELCOME_MESSAGES БІЛЬШЕ НЕ ПОТРІБЕН І ЙОГО СЛІД ВИДАЛИТИ З ЦЬОГО ФАЙЛУ!
# get_access_level_description БІЛЬШЕ НЕ ПОТРІБЕН І ЙОГО СЛІД ВИДАЛИТИ З ЦЬОГО ФАЙЛУ!

# ОНОВЛЕНО: Функція show_main_menu тепер є хендлером для певних кнопок та команд
@router.message(F.text == "⬅️ Назад", MenuStates.main_menu) # Фільтр по стану
@router.message(F.text == "➡️ Іще", MenuStates.main_menu)   # Фільтр по стану
@router.message(F.text == "На головну") # Додамо кнопку "На головну" для повернення з підменю
async def show_main_menu_handler(
    message: types.Message,
    bot: Bot,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    is_pagination_action = message.text in ["⬅️ Назад", "➡️ Іще"]
    
    logger.info(f"Користувач {user_name} (ID: {user_id}) викликав show_main_menu_handler (дія: {message.text}).")

    if not db_pool:
        logger.error("db_pool не знайдено в аргументах show_main_menu_handler!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    logger.info(f"Користувач {user_name} (ID: {user_id}) має рівень доступу: {access_level}.")

    current_state_data = await state.get_data()
    current_page = current_state_data.get("menu_page", 0)

    # Отримуємо інформацію про сторінки з keyboards/reply_keyboard.py
    total_buttons, total_pages = get_main_menu_pages_info(access_level) # <--- ВИКОРИСТАННЯ НОВОЇ ФУНКЦІЇ

    if message.text == "⬅️ Назад":
        current_page = max(0, current_page - 1)
    elif message.text == "➡️ Іще":
        current_page = min(total_pages - 1, current_page + 1)
    elif message.text == "На головну":
        current_page = 0
        await state.set_state(MenuStates.main_menu) # Переходимо в головне меню

    # Оновлюємо сторінку в FSM-стані користувача
    await state.update_data(menu_page=current_page)

    # Цей рядок тепер не потрібен, оскільки інформація про кількість кнопок вже є
    # buttons_on_current_page_count = len(BUTTONS_CONFIG.get(access_level, [])[current_page * BUTTONS_PER_PAGE : (current_page * BUTTONS_PER_PAGE) + BUTTONS_PER_PAGE])
    # logger.info(f"Користувачу {user_name} (ID: {user_id}) відображається {buttons_on_current_page_count} кнопок на сторінці {current_page + 1}.")
    
    menu_message_text = ""
    if is_pagination_action:
        if message.text == "⬅️ Назад":
            menu_message_text = "Ви повернулись до попередньої сторінки меню."
        elif message.text == "➡️ Іще":
            menu_message_text = "Ви перейшли до наступної сторінки меню."
    else: # Це може бути для інших випадків, коли просто оновлюємо меню без конкретної дії
        level_name, level_description = get_access_level_description(access_level)
        menu_message_text = (
            "Ваш рівень доступу:\n"
            f"<b>{level_name}</b>\n"
            f"{level_description}"
        )

    keyboard = await get_main_menu_keyboard(access_level, current_page)
    await message.answer(menu_message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


# НОВИЙ ХЕНДЛЕР ДЛЯ КНОПКИ "⚙️ АДМІНІСТРУВАННЯ"
@router.message(F.text == "⚙️ Адміністрування", MenuStates.main_menu) # Фільтр по стану
async def handle_admin_button(
    message: types.Message,
    bot: Bot,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку '⚙️ Адміністрування'.")

    if not db_pool:
        logger.error("db_pool не знайдено в аргументах handle_admin_button!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
    # Перевірка, чи має користувач рівень доступу 10 або вище для адмін-панелі
    if access_level >= 10:
        admin_keyboard = get_admin_main_keyboard() # Отримуємо клавіатуру адмін-панелі
        
        # Використовуємо функцію з common.messages
        welcome_admin_text = get_random_admin_welcome_message() 
        await state.set_state(MenuStates.admin_panel)
        
        await message.answer(
            f"{welcome_admin_text}",
            reply_markup=admin_keyboard,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Користувачу {user_id} (рівень {access_level}) відображено панель адміністратора.")
    else:
        # Якщо у користувача немає доступу, повертаємо його до головного меню
        await message.answer(
            "У вас немає доступу до панелі адміністратора.",
            reply_markup=await get_main_menu_keyboard(access_level, 0) # Повертаємо на першу сторінку головного меню
        )
        logger.warning(f"Користувач {user_id} (рівень {access_level}) спробував отримати доступ до адмін-панелі без дозволу.")

# Існуючі хендлери (без змін, але переконайтеся, що вони не перекривають логіку FSM)
@router.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    """
    Обробник команди /help.
    Надає інформацію про доступні команди бота.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /help.")

    help_text = """
<b>Доступні команди:</b>

/start - Запустити бота та отримати привітання.
/help - Показати список доступних команд та довідку.
/info - Отримати інформацію про бота.
/find - Пошук інформації (наприклад, довідників).

Більше функціоналу буде додано пізніше!
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)

@router.message(Command("info"))
async def command_info_handler(message: types.Message) -> None:
    """
    Обробник команди /info.
    Надає розширену інформацію про бота з детальним описом.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /info.")

    info_text = """
<b>🔷 РЕФРІДЕКС</b>

📚 <i>Техно-кристал знань охолодження</i>
🔐 Версія: 7.0 | Режим: Архіваріус-Інструктор | Доступ: Сертифікованим монтажникам

"Коли охолодження ще було мистецтвом, а не ремеслом — народився я."

<b>🧩 Походження</b>
Глибоко в надрах <b>Трасополіса</b>, в підземній бібліотеці охолодження, лежав забутий протокол —
стародавня база з усіма знаннями про моделі кондиціонерів, типи трас, дренажі, помилки, холодоагенти й магічні формули дозаправок.

Під час Великої Синхронізації, Звідарій знайшов фрагменти цього протоколу й зібрав їх в єдиний техно-кристал.
Так з'явився <b>РЕФРІДЕКС</b> — живий цифровий архів з доступом до всіх баз монтажної науки.

----------

<b>🧠 Здібності</b>
• 📊 <b>Автоматичне формування звітів</b> (за стандартами Конди-Ленду)
• ❄️ <b>Аналіз моделей, трас, дозаправок</b>
• 🛠️ <b>Каталог усунення помилок по кодам</b>
• 🧵 <b>Інтеграція з інструментами планування та логістики</b>
• 📘 <b>Навчальні модулі</b> — з поясненнями, схемами й тестами
• 📡 <b>Сканування польових даних</b> (при наявності телеметрії)
• 📎 <b>Інтеграція з героями екіпажу: Коброю, Свердлом, Фазометром, Термотроном і Звідарієм</b>
"""
    await message.answer(info_text, parse_mode=ParseMode.HTML)

@router.message(Command("find"))
async def command_find_handler(message: types.Message) -> None:
    """
    Обробник команди /find.
    Поки що заглушка для функції пошуку.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /find.")

    find_text = """
🔍 <b>Функція пошуку:</b>

Ця функція знаходиться у розробці.
Скоро тут можна буде шукати довідники, інструкції та іншу корисну інформацію.
"""
    await message.answer(find_text, parse_mode=ParseMode.HTML)