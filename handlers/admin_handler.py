# handlers/admin_handler.py
import logging
from aiogram import Router, types, F, Bot, Dispatcher
import asyncpg
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone
import random
import asyncio # Додано для sys.exit() і asyncio.sleep()
import sys     # Додано для sys.exit()

# Імпортуємо загальні клавіатури з пакету keyboards
from keyboards import get_main_menu_keyboard

# Імпортуємо адмінські клавіатури з модуля admin_keyboard
from keyboards.admin_keyboard import (
    get_admin_main_keyboard,
    get_users_list_keyboard,
    get_user_actions_keyboard,
    get_access_level_keyboard,
    ACCESS_LEVEL_BUTTONS
)

# !!! ВИПРАВЛЕНО ШЛЯХ ДО ІМПОРТУ БАЗИ ДАНИХ !!!
from database.users_db import get_user, add_user, update_user_activity, get_user_access_level, get_all_users, update_user_authorization_status

# --- СПИСОК ВІТАЛЬНИХ ПОВІДОМЛЕНЬ ДЛЯ СПИСКУ КОРИСТУВАЧІВ ---
USER_LIST_MESSAGES = [
    "<b>🧾 Refridex OS:</b>\n “Сканування активних ID завершено. Обери ціль зі списку.”",
    "<b>📂 Refridex OS:</b>\n “Інтерфейс користувачів ініціалізовано. Обери суб’єкта керування.”",
    "<b>🔍 Refridex OS:</b>\n “Доступні персональні ядра. Підключення до одного — на твій вибір.”",
    "<b>👤 Refridex OS:</b>\n “Виявлено облікові одиниці. Обери об'єкт взаємодії зі списку.”",
    "<b>📡 Refridex OS:</b>\n “Модуль користувачів розгорнуто. Обери ідентифікатор.”",
    "<b>🧬 Refridex OS:</b>\n “Список аватарів системи готовий до дій. Обери напрямок контролю.”",
    "<b>💠 Refridex OS:</b>\n “Цифрові сигнатури активні. Кого просканувати далі?”",
    "<b>📜 Refridex OS:</b>\n “Індекс користувачів завантажено. Розпочни взаємодію.”",
    "<b>🕹️ Refridex OS:</b>\n “Об’єкти керування доступні. Система очікує вибору.”",
    "<b>📊 Refridex OS:</b>\n “Активовано перегляд користувачів. Обери одиницю для дій.”"
]
# -----------------------------------------------------------

# --- СПИСОК ПОВІДОМЛЕНЬ ПРИ ПОВЕРНЕННІ ДО АДМІН-МЕНЮ ---
ADMIN_RETURN_MESSAGES = [
    "🧠 Refridex OS:\nСеанс відновлено успішно.\n🔁 Ви знову перебуваєте в головному меню адміністратора.\n⌁ Очікую подальших інструкцій…",
    "🧠 Refridex OS:\nАдмін-доступ підтверджено.\n🛡️ Панель команд активна.\n⌁ Час керувати Конди-Лендом.",
    "🧠 Refridex OS:\nПовернення у контрольний центр виконано.\n🔧 Системні шини стабільні.\n⌁ Готовий до маніпуляцій.",
    "🧠 Refridex OS:\nОператор у системі.\n☑️ Протоколи безпеки пройдено.\n⌁ Чекаю на ваш наступний хід.",
    "🧠 Refridex OS:\nВи знову біля ядра.\n🧬 Права доступу рівня адміністратора активовано.\n⌁ Сканую можливі дії…",
    "🧠 Refridex OS:\nКонтроль повернуто.\n📊 Інтерфейс головного меню готовий до обробки запитів.\n⌁ Виберіть команду.",
    "🧠 Refridex OS:\nАдміністративна панель розблокована.\n⚙️ Прив'язка до профілю — підтверджена.\n⌁ Ядро в режимі очікування.",
    "🧠 Refridex OS:\n🔄 Перехід завершено.\nВи в головному меню адміністратора.\n⌁ Підсистема слухає.",
    "🧠 Refridex OS:\nВхід до адмін-терміналу завершено.\n🛠️ Інтерфейс оновлено.\n⌁ Система приймає команди.",
    "🧠 Refridex OS:\nСигнал перевірено.\n🎛️ Головне меню адміністратора завантажено.\n⌁ Запуск команд — у вашому розпорядженні.",
    "🧠 Refridex OS:\nЗ'єднання з панеллю підтверджено.\n📡 Рівень доступу: ROOT.\n⌁ Час діяти, командире.",
    "🧠 Refridex OS:\nДобре повернутись, адміністраторе.\n🔐 Ваше місце за пультом контролю.\n⌁ Конди-світло готове до вашої волі.",
    "🧠 Refridex OS:\nПорт керування відкрито.\n🧭 Ви в адміністративному модулі.\n⌁ Направляйте систему.",
    "🧠 Refridex OS:\nВітаю в епіцентрі управління.\n⚡️ Система повністю в онлайні.\n⌁ Чекаю на вхідну команду.",
    "🧠 Refridex OS:\nОпераційна лінія активна.\n🎯 Панель адміністратора виведено на передній план.\n⌁ Введіть наступну дію."
]
# -----------------------------------------------------------

try:
    from telethon_client import get_telethon_status, get_dialogs_list_telethon, TelethonClientManager
except ImportError:
    logging.warning("Telethon client not found. Telethon related functions will be disabled.")
    async def get_telethon_status(client=None) -> str:
        return "❓ Telethon не завантажено або не підключено."
    async def get_dialogs_list_telethon(client=None) -> list:
        return []
    class TelethonClientManager:
        def __init__(self, db_pool):
            self.client = None
            self.db_pool = db_pool
        async def start_client(self): pass
        async def disconnect_client(self): pass
        async def authorize_client(self, phone_number): return False
        async def sign_in_client(self, code, password=None): return False
        async def get_client(self): return None
        # Додані заглушки для нових методів
        async def is_client_connected(self): return False
        def get_session_name(self): return "N/A"
        def get_phone_number(self): return "N/A"
        def get_user_id(self): return "N/A"
        def get_session_hash(self): return "N/A"


logger = logging.getLogger(__name__)
router = Router()
user_list_pages = {}

# --- NEW HANDLER FOR CONNECTION STATUS ---
@router.callback_query(F.data == "admin_connection_status")
async def process_connection_status(callback: types.CallbackQuery, telethon_manager: TelethonClientManager, db_pool_instance: asyncpg.Pool):
    user_id = callback.from_user.id
    current_message = callback.message

    logger.info(f"Адміністратор {user_id} запитав статус підключення.")

    # Перевірка рівня доступу
    access_level = await get_user_access_level(db_pool_instance, user_id)
    if access_level < 10: # Припускаємо, що рівень 10 (Адміністратор Ядра) або вище може перевіряти статус
        await callback.answer("У вас недостатньо прав для перегляду статусу зв'язку.", show_alert=True)
        logger.warning(f"Користувач {user_id} (рівень {access_level}) намагався переглянути статус підключення без достатніх прав.")
        return

    await current_message.edit_text("📡 ReLink: Зчитую дані каналу зв'язку... Будь ласка, зачекайте.")

    status_text = "📊 **ReLink: Статус каналу зв'язку**\n\n"
    connection_successful = True

    try:
        # Перевірка статусу Telethon
        is_connected = await telethon_manager.is_client_connected()
        session_name = telethon_manager.get_session_name()
        phone_number = telethon_manager.get_phone_number()

        status_text += f"▪️ **Telethon:** "
        if is_connected:
            status_text += "✅ **Підключено**\n"
            status_text += f"  • Ім'я сесії: `{session_name}`\n"
            status_text += f"  • Номер телефону: `{phone_number if phone_number else 'Не визначено'}`\n"
            status_text += f"  • ID користувача Telethon: `{telethon_manager.get_user_id() if telethon_manager.get_user_id() else 'Не визначено'}`\n"
            status_text += f"  • Хеш сесії: `{telethon_manager.get_session_hash()[:8]}...`\n" # Показуємо перші 8 символів хешу
        else:
            status_text += "❌ **Відключено**\n"
            status_text += "  • Рекомендація: Запустіть авторизацію TeleKey.\n"
            connection_successful = False

        # Тут можна додати перевірку інших підключень або сервісів

        # Додамо загальний статус
        if connection_successful:
            status_text += "\n🌟 **Загальний стан:** Всі основні системи зв'язку працюють стабільно."
        else:
            status_text += "\n⚠️ **Загальний стан:** Виявлені проблеми з підключеннями. Рекомендується перевірка."

    except Exception as e:
        status_text = f"❌ **ReLink: Помилка при отриманні статусу зв'язку!**\n"
        status_text += f"Деталі: `{e}`\n"
        status_text += "\nБудь ласка, зверніться до розробника."
        logger.error(f"Помилка при перевірці статусу підключення: {e}", exc_info=True)

    await current_message.edit_text(status_text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")
    await callback.answer() # Завершуємо обробку callback-запиту
# --- END NEW HANDLER ---

# --- NEW HANDLER FOR BOT RESTART ---
@router.callback_query(F.data == "admin_restart_bot") # Це callback, який ви додасте в клавіатуру
async def admin_restart_bot_handler(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot

    logger.info(f"Адміністратор {user_id} запросив перезапуск бота.")

    # Перевірка рівня доступу адміністратора (необхідно для безпеки)
    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для admin_restart_bot_handler!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    admin_access_level = await get_user_access_level(db_pool, user_id)
    if admin_access_level < 100: # Припускаємо, що 100 - це рівень супер-адміна (Архітектор Системи)
        await callback_query.answer("У вас недостатньо прав для цієї дії.", show_alert=True)
        logger.warning(f"Користувач {user_id} (рівень {admin_access_level}) намагався перезапустити бота без достатніх прав.")
        return

    try:
        restart_message = "🔄 Refridex OS: Запускаю протокол 'Перезапуск системи'.\nОчікуйте, відновлення зв'язку відбудеться за декілька секунд..."
        await callback_query.message.edit_text(restart_message)
        await callback_query.answer("Запит на перезапуск надіслано.", show_alert=False)
        logger.info(f"Надіслано повідомлення про перезапуск користувачу {user_id}.")

        # Важливо: Завершити всі асинхронні операції та закрити з'єднання
        if db_pool:
            logger.info("Закриваю пул з'єднань до БД...")
            await db_pool.close()
            logger.info("Пул з'єднань до БД закрито.")

        # Якщо у вас є менеджер Telethon, який потрібно відключити перед виходом
        telethon_manager = dispatcher.workflow_data.get('telethon_manager')
        if telethon_manager:
            logger.info("Відключаю Telethon клієнта...")
            await telethon_manager.disconnect_client()
            logger.info("Telethon клієнт відключений.")

        # Невеликий таймаут, щоб Telegram встиг обробити останнє повідомлення
        await asyncio.sleep(1)

        logger.critical(f"Бот ініціює вихід для перезапуску за запитом адміністратора {user_id}.")
        sys.exit(0) # Завершуємо процес бота

    except Exception as e:
        logger.error(f"Помилка при ініціації перезапуску бота для {user_id}: {e}", exc_info=True)
        await callback_query.message.answer("Виникла помилка під час спроби перезапуску. Перевірте логи.")
        await callback_query.answer("Помилка перезапуску.", show_alert=True)
# --- END NEW HANDLER FOR BOT RESTART ---


@router.callback_query(F.data == "admin_show_users")
async def admin_show_users_handler(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot
    logger.info(f"!!! Спрацював обробник admin_show_users_handler для {callback_query.from_user.id} !!!")
    logger.info(f"DB Pool: {db_pool is not None}, Bot: {bot is not None}")
    logger.info(f"Callback data: {callback_query.data}")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для admin_show_users_handler!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    users = await get_all_users(db_pool)
    logger.info(f"Отримано {len(users)} користувачів з БД.")

    user_list_pages[callback_query.from_user.id] = 0
    current_page = user_list_pages[callback_query.from_user.id]
    users_per_page = 5
    total_users = len(users)
    total_pages = (total_users + users_per_page - 1) // users_per_page if total_users > 0 else 1

    user_list_welcome_text = random.choice(USER_LIST_MESSAGES)

    response_text = ""
    reply_markup = None

    if not users:
        response_text = "Наразі немає зареєстрованих користувачів."
        reply_markup = get_admin_main_keyboard()
        logger.warning(f"Користувач {callback_query.from_user.id} запросив список користувачів, але їх немає.")
    else:
        response_text = (
            f"{user_list_welcome_text}\n\n"
            f"<i>(стор. {current_page + 1}/{total_pages}):</i>"
        )
        reply_markup = get_users_list_keyboard(users, current_page, users_per_page)
        logger.info(f"Користувачу {callback_query.from_user.id} відображено список користувачів на сторінці {current_page + 1}.")

    try:
        await callback_query.message.edit_text(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Помилка при оновленні повідомлення для списку користувачів {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.message.answer(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    await callback_query.answer()

@router.callback_query(F.data == "cancel_admin_action")
async def cancel_admin_action_handler(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id = callback_query.from_user.id
    logger.info(f"Користувач {user_id} натиснув '⬅️ Назад до адмін-меню'.")

    # Вибираємо випадкове повідомлення зі списку
    return_message = random.choice(ADMIN_RETURN_MESSAGES)

    try:
        await callback_query.message.edit_text(
            return_message, # Використовуємо рандомне повідомлення
            parse_mode='HTML',
            reply_markup=get_admin_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Помилка при поверненні до адмін-меню для користувача {user_id}: {e}", exc_info=True)
        await callback_query.message.answer(
            return_message, # Використовуємо рандомне повідомлення
            parse_mode='HTML',
            reply_markup=get_admin_main_keyboard()
        )
    await callback_query.answer()

@router.callback_query(F.data.startswith("page_"))
async def paginate_users_list(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для paginate_users_list!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    new_page = int(callback_query.data.split('_')[1])
    user_list_pages[user_id] = new_page

    users = await get_all_users(db_pool)
    users_per_page = 5
    total_users = len(users)
    total_pages = (total_users + users_per_page - 1) // users_per_page if total_users > 0 else 1

    user_list_welcome_text = random.choice(USER_LIST_MESSAGES)

    if not users:
        response_text = "Наразі немає зареєстрованих користувачів."
        reply_markup = get_admin_main_keyboard()
    else:
        response_text = (
            f"{user_list_welcome_text}\n\n"
            f"<b>Оберіть користувача зі списку (стор. {new_page + 1}/{total_pages}):</b>"
        )
        reply_markup = get_users_list_keyboard(users, new_page, users_per_page)

    try:
        await callback_query.message.edit_text(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Помилка при пагінації списку користувачів для {user_id}: {e}", exc_info=True)
        await callback_query.message.answer(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    await callback_query.answer()

@router.callback_query(F.data.startswith("user_"))
async def show_user_management_menu(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id_to_manage = int(callback_query.data.split('_')[1])
    current_admin_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot

    logger.info(f"Адміністратор {current_admin_id} обрав користувача {user_id_to_manage} для керування.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для show_user_management_menu!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    user_info = await get_user(db_pool, user_id_to_manage)
    if not user_info:
        logger.warning(f"Спроба керувати неіснуючим користувачем {user_id_to_manage} адміністратором {current_admin_id}.")
        await callback_query.answer("Користувача не знайдено.", show_alert=True)
        await admin_show_users_handler(callback_query, dispatcher)
        return

    is_authorized = user_info.get('is_authorized', False)
    access_level = user_info.get('access_level', 0)

    access_level_display_name = "Невідомий рівень"
    for level, name in ACCESS_LEVEL_BUTTONS:
        if level == access_level:
            access_level_display_name = name
            break

    status_text = "Авторизований ✅" if is_authorized else "Неавторизований ❌"

    # !!! ВИПРАВЛЕНО: Використання 'registered_at' для дати реєстрації !!!
    registered_at_dt = user_info.get('registered_at', datetime.now(timezone.utc))
    last_activity_dt = user_info.get('last_activity', datetime.now(timezone.utc))

    registered_at_str = registered_at_dt.strftime('%d.%m.%Y / %H:%M')
    last_activity_str = last_activity_dt.strftime('%d.%m.%Y / %H:%M')

    response_text = (
        f"<b>🧾 ID-ключ:</b> <code>{user_id_to_manage}</code>\n"
        f"<b>🧑‍🚀 Агент:</b> {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
        f"<b>💬 Позивний:</b> @{user_info.get('username', 'N/A')}\n"
        f"<b>🛡️ Протокол доступу:</b> {access_level_display_name}\n"
        f"<b>📶 Статус:</b> {status_text}\n"
        f"<b>📥 Занесено в систему:</b> {registered_at_str}\n"
        f"<b>📈 Остання активність:</b> {last_activity_str}\n"
        f"☰☱☲☳☴☵☶☷☰☱☲☳☴☵☶☷☰☱☲☳\n"
        f"<b>📡 Командний центр активний. Очікується інструкція…</b>"
    )

    reply_markup = get_user_actions_keyboard(is_authorized, access_level, user_id_to_manage)

    try:
        await callback_query.message.edit_text(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Помилка при відображенні меню управління користувачем {user_id_to_manage}: {e}", exc_info=True)
        await callback_query.message.answer(
            response_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    await callback_query.answer()


@router.callback_query(F.data.startswith("change_access_level_"))
async def request_change_access_level(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id_to_manage = int(callback_query.data.split('_')[3])
    admin_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')

    logger.info(f"Користувач {admin_id} запросив зміну рівня доступу для {user_id_to_manage}.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для request_change_access_level!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    user_info = await get_user(db_pool, user_id_to_manage)

    user_name_display = f"ID: {user_id_to_manage}"
    if user_info:
        first_name = user_info.get('first_name')
        last_name = user_info.get('last_name')

        if first_name and last_name:
            user_name_display = f"{first_name} {last_name} (ID: {user_id_to_manage})"
        elif first_name:
            user_name_display = f"{first_name} (ID: {user_id_to_manage})"

    reply_markup = get_access_level_keyboard(user_id_to_manage)

    try:
        await callback_query.message.edit_text(
            f"Оберіть новий рівень доступу для користувача <b>{user_name_display}</b>:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Помилка при запиті зміни рівня доступу для {user_id_to_manage}: {e}", exc_info=True)
        await callback_query.message.answer(
            f"Оберіть новий рівень доступу для користувача <b>{user_name_display}</b>:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    await callback_query.answer()

@router.callback_query(F.data.startswith("set_access_level_"))
async def set_new_access_level(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    parts = callback_query.data.split('_')
    new_level = int(parts[3])
    user_id_to_manage = int(parts[4])
    admin_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot

    logger.info(f"Адміністратор {admin_id} встановлює рівень доступу {new_level} для користувача {user_id_to_manage}.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для set_new_access_level!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET access_level = $1 WHERE id = $2",
                new_level,
                user_id_to_manage
            )
        await callback_query.answer(f"Рівень доступу користувача {user_id_to_manage} змінено на {new_level}.", show_alert=True)
        logger.info(f"Рівень доступу користувача {user_id_to_manage} змінено на {new_level} адміністратором {admin_id}.")

        user_info = await get_user(db_pool, user_id_to_manage)
        if not user_info:
            logger.warning(f"Користувача {user_id_to_manage} не знайдено після зміни рівня доступу. Неможливо оновити інтерфейс.")
            return

        is_authorized = user_info.get('is_authorized', False)
        access_level = user_info.get('access_level', 0)

        access_level_display_name = "Невідомий рівень"
        for level, name in ACCESS_LEVEL_BUTTONS:
            if level == access_level:
                access_level_display_name = name
                break

        status_text = "Авторизований ✅" if is_authorized else "Неавторизований ❌"

        # !!! ВИПРАВЛЕНО: Використання 'registered_at' для дати реєстрації !!!
        registered_at_dt = user_info.get('registered_at', datetime.now(timezone.utc))
        last_activity_dt = user_info.get('last_activity', datetime.now(timezone.utc))

        registered_at_str = registered_at_dt.strftime('%d.%m.%Y / %H:%M')
        last_activity_str = last_activity_dt.strftime('%d.%m.%Y / %H:%M')

        response_text = (
            f"<b>🧾 ID-ключ:</b> <code>{user_id_to_manage}</code>\n"
            f"<b>🧑‍🚀 Агент:</b> {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
            f"<b>💬 Позивний:</b> @{user_info.get('username', 'N/A')}\n"
            f"<b>🛡️ Протокол доступу:</b> {access_level_display_name}\n"
            f"<b>📶 Статус:</b> {status_text}\n"
            f"<b>📥 Занесено в систему:</b> {registered_at_str}\n"
            f"<b>📈 Остання активність:</b> {last_activity_str}\n"
            f"☰☱☲☳☴☵☶☷☰☱☲☳☴☵☶☷☰☱☲☳\n"
            f"<b>📡 Командний центр активний. Очікується інструкція…</b>"
        )

        reply_markup = get_user_actions_keyboard(is_authorized, access_level, user_id_to_manage)

        try:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=response_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.info(f"Оновлено меню управління для користувача {user_id_to_manage} після зміни рівня.")
        except Exception as edit_e:
            logger.error(f"Помилка при оновленні повідомлення управління користувачем {user_id_to_manage} після зміни рівня: {edit_e}", exc_info=True)
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=response_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.warning(f"Відправлено нове повідомлення замість редагування для користувача {user_id_to_manage} після зміни рівня.")

    except Exception as e:
        logger.error(f"Глобальна помилка в set_new_access_level для користувача {user_id_to_manage}: {e}", exc_info=True)
        await callback_query.answer("Помилка при зміні рівня доступу.", show_alert=True)
        user_info = await get_user(db_pool, user_id_to_manage)
        if user_info:
            is_authorized = user_info.get('is_authorized', False)
            access_level = user_info.get('access_level', 0)

            access_level_display_name = "Невідомий рівень"
            for level, name in ACCESS_LEVEL_BUTTONS:
                if level == access_level:
                    access_level_display_name = name
                    break

            status_text = "Авторизований ✅" if is_authorized else "Неавторизований ❌"

            # !!! ВИПРАВЛЕНО: Використання 'registered_at' для дати реєстрації !!!
            registered_at_dt = user_info.get('registered_at', datetime.now(timezone.utc))
            last_activity_dt = user_info.get('last_activity', datetime.now(timezone.utc))

            registered_at_str = registered_at_dt.strftime('%d.%m.%Y / %H:%M')
            last_activity_str = last_activity_dt.strftime('%d.%m.%Y / %H:%M')

            response_text_error = (
                f"<b>🧾 ID-ключ:</b> <code>{user_id_to_manage}</code>\n"
                f"<b>🧑‍🚀 Агент:</b> {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                f"<b>💬 Позивний:</b> @{user_info.get('username', 'N/A')}\n"
                f"<b>🛡️ Протокол доступу:</b> {access_level_display_name}\n"
                f"<b>📶 Статус:</b> {status_text}\n"
                f"<b>📥 Занесено в систему:</b> {registered_at_str}\n"
                f"<b>📈 Остання активність:</b> {last_activity_str}\n"
                f"☰☱☲☳☴☵☶☷☰☱☲☳☴☵☶☷☰☱☲☳\n"
                f"<b>📡 Командний центр активний. Очікується інструкція…</b>"
            )
            reply_markup_error = get_user_actions_keyboard(is_authorized, access_level, user_id_to_manage)
            try:
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=response_text_error,
                    parse_mode='HTML',
                    reply_markup=reply_markup_error
                )
            except Exception as final_e:
                logger.error(f"ФІНАЛЬНА ПОМИЛКА: Не вдалося оновити/відправити повідомлення після помилки зміни рівня доступу для {user_id_to_manage}: {final_e}", exc_info=True)

# !!! ДОДАНО НОВИЙ ОБРОБНИК ДЛЯ АВТОРИЗАЦІЇ/ДЕАВТОРИЗАЦІЇ !!!
@router.callback_query(F.data.startswith(("unauthorize_user_", "authorize_user_")))
async def toggle_user_authorization(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    parts = callback_query.data.split('_')

    # Визначаємо дію та user_id_to_manage на основі префіксу
    if parts[0] == "unauthorize":
        action = "deauthorize"
        user_id_to_manage = int(parts[2])
    elif parts[0] == "authorize":
        action = "authorize"
        user_id_to_manage = int(parts[2])
    else:
        logger.error(f"Невідомий формат callback_data для toggle_user_authorization: {callback_query.data}")
        await callback_query.answer("Невідома дія.", show_alert=True)
        return

    admin_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot

    logger.info(f"Адміністратор {admin_id} намагається {action} користувача {user_id_to_manage}.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для toggle_user_authorization!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    is_authorized_status = True if action == "authorize" else False

    try:
        await update_user_authorization_status(db_pool, user_id_to_manage, is_authorized_status)

        status_message = "авторизовано" if is_authorized_status else "деавторизовано"
        await callback_query.answer(f"Користувача {user_id_to_manage} успішно {status_message}.", show_alert=True)
        logger.info(f"Користувача {user_id_to_manage} успішно {status_message} адміністратором {admin_id}.")

        # Оновлення інтерфейсу користувача після зміни статусу
        user_info = await get_user(db_pool, user_id_to_manage)
        if not user_info:
            logger.warning(f"Користувача {user_id_to_manage} не знайдено після зміни статусу авторизації. Неможливо оновити інтерфейс.")
            return

        is_authorized = user_info.get('is_authorized', False)
        access_level = user_info.get('access_level', 0)

        access_level_display_name = "Невідомий рівень"
        for level, name in ACCESS_LEVEL_BUTTONS:
            if level == access_level:
                access_level_display_name = name
                break

        status_text = "Авторизований ✅" if is_authorized else "Неавторизований ❌"

        # !!! ВИПРАВЛЕНО: Використання 'registered_at' для дати реєстрації !!!
        registered_at_dt = user_info.get('registered_at', datetime.now(timezone.utc))
        last_activity_dt = user_info.get('last_activity', datetime.now(timezone.utc))

        registered_at_str = registered_at_dt.strftime('%d.%m.%Y / %H:%M')
        last_activity_str = last_activity_dt.strftime('%d.%m.%Y / %H:%M')

        response_text = (
            f"<b>🧾 ID-ключ:</b> <code>{user_id_to_manage}</code>\n"
            f"<b>🧑‍🚀 Агент:</b> {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
            f"<b>💬 Позивний:</b> @{user_info.get('username', 'N/A')}\n"
            f"<b>🛡️ Протокол доступу:</b> {access_level_display_name}\n"
            f"<b>📶 Статус:</b> {status_text}\n"
            f"<b>📥 Занесено в систему:</b> {registered_at_str}\n"
            f"<b>📈 Остання активність:</b> {last_activity_str}\n"
            f"☰☱☲☳☴☵☶☷☰☱☲☳☴☵☶☷☰☱☲☳\n"
            f"<b>📡 Командний центр активний. Очікується інструкція…</b>"
        )
        reply_markup = get_user_actions_keyboard(is_authorized, access_level, user_id_to_manage)

        try:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=response_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.info(f"Оновлено меню управління для користувача {user_id_to_manage} після зміни авторизації.")
        except Exception as edit_e:
            logger.error(f"Помилка при оновленні повідомлення управління користувачем {user_id_to_manage} після зміни авторизації: {edit_e}", exc_info=True)
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=response_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.warning(f"Відправлено нове повідомлення замість редагування для користувача {user_id_to_manage} після зміни авторизації.")

    except Exception as e:
        logger.error(f"Помилка при зміні статусу авторизації для користувача {user_id_to_manage}: {e}", exc_info=True)
        await callback_query.answer("Помилка при зміні статусу авторизації.", show_alert=True)
        user_info = await get_user(db_pool, user_id_to_manage)
        if user_info:
            is_authorized = user_info.get('is_authorized', False)
            access_level = user_info.get('access_level', 0)
            access_level_display_name = "Невідомий рівень"
            for level, name in ACCESS_LEVEL_BUTTONS:
                if level == access_level:
                    access_level_display_name = name
                    break
            status_text = "Авторизований ✅" if is_authorized else "Неавторизований ❌"

            # !!! ВИПРАВЛЕНО: Використання 'registered_at' для дати реєстрації !!!
            registered_at_dt = user_info.get('registered_at', datetime.now(timezone.utc))
            last_activity_dt = user_info.get('last_activity', datetime.now(timezone.utc))

            registered_at_str = registered_at_dt.strftime('%d.%m.%Y / %H:%M')
            last_activity_str = last_activity_dt.strftime('%d.%m.%Y / %H:%M')

            response_text_error = (
                f"<b>🧾 ID-ключ:</b> <code>{user_id_to_manage}</code>\n"
                f"<b>🧑‍🚀 Агент:</b> {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                f"<b>💬 Позивний:</b> @{user_info.get('username', 'N/A')}\n"
                f"<b>🛡️ Протокол доступу:</b> {access_level_display_name}\n"
                f"<b>📶 Статус:</b> {status_text}\n"
                f"<b>📥 Занесено в систему:</b> {registered_at_str}\n"
                f"<b>📈 Остання активність:</b> {last_activity_str}\n"
                f"☰☱☲☳☴☵☶☷☰☱☲☳☴☵☶☷☰☱☲☳\n"
                f"<b>📡 Командний центр активний. Очікується інструкція…</b>"
            )
            reply_markup_error = get_user_actions_keyboard(is_authorized, access_level, user_id_to_manage)
            try:
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=response_text_error,
                    parse_mode='HTML',
                    reply_markup=reply_markup_error
                )
            except Exception as final_e:
                logger.error(f"ФІНАЛЬНА ПОМИЛКА: Не вдалося оновити/відправити повідомлення після помилки зміни статусу авторизації для {user_id_to_manage}: {final_e}", exc_info=True)


@router.callback_query(F.data == "close_admin_panel")
async def close_admin_panel(callback_query: types.CallbackQuery, dispatcher: Dispatcher) -> None:
    user_id = callback_query.from_user.id
    db_pool = dispatcher.workflow_data.get('db_pool_instance')
    bot = callback_query.bot

    logger.info(f"Користувач {user_id} закриває панель адміністратора.")

    if not db_pool:
        logger.error("db_pool_instance не знайдено в workflow_data для close_admin_panel!")
        await callback_query.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)

    try:
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
        )
        logger.info(f"Видалено повідомлення з адмін-панеллю для {user_id}.")

        # Вибираємо випадкове повідомлення зі списку при закритті адмін-панелі
        return_message = random.choice(ADMIN_RETURN_MESSAGES)

        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=return_message, # Використовуємо рандомне повідомлення
            parse_mode='HTML',
            reply_markup=await get_main_menu_keyboard(access_level, user_list_pages.get(user_id, 0))
        )
        logger.info(f"Відправлено головне меню для {user_id} після закриття адмін-панелі.")

    except Exception as e:
        logger.error(f"Помилка при закритті адмін-панелі для користувача {user_id}: {e}", exc_info=True)
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Виникла проблема при закритті панелі. Повернуто до головного меню.", # Статичне повідомлення у випадку помилки
            reply_markup=await get_main_menu_keyboard(access_level, user_list_pages.get(user_id, 0))
        )
    await callback_query.answer()