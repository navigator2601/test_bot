# handlers/admin/telethon_operations.py

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from database.users_db import get_user_access_level
from common.telethon_states import TelethonAuthStates

# <--- ЗМІНА ТУТ: Оновлені імпорти клавіатур
from keyboards.admin_keyboard import get_admin_main_keyboard, get_telethon_actions_keyboard # Змінено admin_main_menu_keyboard на get_admin_main_keyboard
# telethon_api_menu_keyboard та telethon_login_keyboard тут не імпортуються, оскільки їх немає в admin_keyboard.py
# Натомість, ми будемо використовувати get_telethon_actions_keyboard та створимо тимчасову клавіатуру для входу

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "admin_telethon_api")
async def show_telethon_api_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = "🔐 **TeleKey · Авторизація API-зв’язку**\n\n" \
           "Тут ви можете керувати сесіями Telethon клієнтів. " \
           "Це дозволить боту взаємодіяти з Telegram від імені іншого облікового запису."
    # <--- ЗМІНА ТУТ: Використовуємо get_telethon_actions_keyboard
    await callback.message.edit_text(text, reply_markup=get_telethon_actions_keyboard()) 
    logger.info(f"Користувач {callback.from_user.id} натиснув '🔐 TeleKey · Авторизація API-зв’язку'.")


@router.callback_query(F.data == "telethon_auth_status")
async def check_telethon_status(callback: CallbackQuery, telethon_manager, db_pool):
    await callback.answer("Перевіряю статус Telethon сесій...", cache_time=1)
    logger.info(f"Користувач {callback.from_user.id} перевіряє статус Telethon.")

    active_clients_count = len(telethon_manager.get_all_active_clients())
    
    # Можна також перевірити, чи є сесії в БД, які ще не активні
    db_sessions = await db_pool.fetch("SELECT phone_number FROM telethon_sessions")
    db_sessions_count = len(db_sessions)

    text = f"🌐 **Статус Telethon сесій**\n\n" \
           f"✅ Активних підключень: `{active_clients_count}`\n" \
           f"🗄️ Збережених сесій у БД: `{db_sessions_count}`"

    if active_clients_count > 0:
        text += "\n\n**Активні номери:**\n"
        for phone, client in telethon_manager.get_all_active_clients().items():
            try:
                # Це асинхронний виклик, тому його краще зробити окремо, якщо потрібно більше деталей
                # Уникнемо його тут, щоб не уповільнювати інтерфейс, якщо активних клієнтів багато
                pass 
            except Exception:
                pass
            text += f"- `{phone}`\n"
    else:
        text += "\n\n*Наразі активних Telethon клієнтів немає.*"

    # <--- ЗМІНА ТУТ: Використовуємо get_telethon_actions_keyboard
    await callback.message.edit_text(text, reply_markup=get_telethon_actions_keyboard())


@router.callback_query(F.data == "telethon_authorize") # Цей callback_data, ймовірно, має бути "telethon_start_auth"
async def start_telethon_authorization(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # <--- ДОДАНО ТУТ: Створюємо просту клавіатуру для скасування входу, оскільки telethon_login_keyboard відсутня
    login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
    ])

    await callback.message.edit_text("📞 **Авторизація Telethon**\n\n"
                                     "Будь ласка, введіть номер телефону для авторизації (наприклад, `+380XXXXXXXXX`):",
                                     reply_markup=login_keyboard) # <--- ЗМІНА ТУТ: Використовуємо тимчасову клавіатуру
    await state.set_state(TelethonAuthStates.waiting_for_phone_number) 
    logger.info(f"Користувач {callback.from_user.id} ініціював авторизацію Telethon.")


@router.message(TelethonAuthStates.waiting_for_phone_number) 
async def handle_telethon_input(message: Message, state: FSMContext, telethon_manager, db_pool):
    phone_number = message.text.strip()

    if not phone_number.startswith('+') or not phone_number[1:].isdigit():
        # <--- ДОДАНО ТУТ: Клавіатура для відповіді про помилку
        login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
        ])
        await message.reply("Невірний формат номера телефону. Будь ласка, введіть у форматі `+380XXXXXXXXX`.", reply_markup=login_keyboard)
        return

    await state.update_data(phone_number=phone_number)

    try:
        session_string = await telethon_manager.load_session_from_db(phone_number, db_pool)
        
        if session_string:
            client = TelegramClient(StringSession(session_string), telethon_manager.api_id, telethon_manager.api_hash)
            logger.info(f"Завантажено StringSession для {phone_number} з БД.")
        else:
            client = TelegramClient(StringSession(), telethon_manager.api_id, telethon_manager.api_hash)
            logger.info(f"Створено новий TelethonClient для {phone_number} (без збереженої сесії).")

        telethon_manager.add_client(phone_number, client)

        # <--- ДОДАНО ТУТ: Клавіатура для відповіді про відправку коду
        login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
        ])
        await message.reply(f"Спроба відправки коду авторизації для {phone_number}...", reply_markup=login_keyboard)
        logger.info(f"Спроба відправки коду авторизації для {phone_number}...")

        await client.connect()
        if not await client.is_user_authorized():
            try:
                phone_code_hash = (await client.send_code_request(phone_number)).phone_code_hash
                await state.update_data(phone_code_hash=phone_code_hash)
                await message.reply("Будь ласка, введіть код, який ви отримали в Telegram:", reply_markup=login_keyboard)
                await state.set_state(TelethonAuthStates.waiting_for_code)
            except Exception as e:
                logger.error(f"Помилка відправки коду для {phone_number}: {e}", exc_info=True)
                await message.reply(f"Помилка відправки коду: {e}. Спробуйте ще раз або перевірте номер телефону.", reply_markup=login_keyboard)
                await state.set_state(None)
                if phone_number in telethon_manager.clients:
                    await telethon_manager.clients[phone_number].disconnect()
                    telethon_manager.clients.pop(phone_number)
                return
        else:
            await telethon_manager.save_session_to_db(phone_number, client, db_pool)
            await message.reply(f"Клієнт {phone_number} вже авторизовано.", reply_markup=get_telethon_actions_keyboard())
            await state.set_state(None)

    except Exception as e:
        logger.error(f"Непередбачена помилка в handle_telethon_input: {e}", exc_info=True)
        # <--- ДОДАНО ТУТ: Клавіатура для відповіді про помилку
        login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
        ])
        await message.reply(f"Виникла непередбачена помилка: {e}. Будь ласка, спробуйте ще раз.", reply_markup=login_keyboard)
        await state.set_state(None)
        if phone_number in telethon_manager.clients:
            await telethon_manager.clients[phone_number].disconnect()
            telethon_manager.clients.pop(phone_number)


@router.message(TelethonAuthStates.waiting_for_code) 
async def handle_telethon_code(message: Message, state: FSMContext, telethon_manager, db_pool):
    code = message.text.strip()
    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    phone_code_hash = user_data.get('phone_code_hash')

    # <--- ДОДАНО ТУТ: Клавіатура для відповідей
    login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
    ])

    if not phone_number or not phone_code_hash:
        await message.reply("Сталася помилка. Будь ласка, почніть авторизацію знову.", reply_markup=login_keyboard)
        await state.set_state(None)
        return

    client = telethon_manager.get_client(phone_number)
    if not client:
        await message.reply("Клієнт Telethon не знайдено. Будь ласка, почніть авторизацію знову.", reply_markup=login_keyboard)
        await state.set_state(None)
        return

    try:
        await client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
        await telethon_manager.save_session_to_db(phone_number, client, db_pool)
        
        me = await client.get_me()
        await message.reply(f"✅ Успішно авторизовано клієнта {phone_number} як **{me.first_name}** (ID: {me.id}).", reply_markup=get_telethon_actions_keyboard())
        logger.info(f"Клієнт {phone_number} успішно авторизовано як {me.first_name} (ID: {me.id}).")
        await state.set_state(None)
        # Не викликаємо show_telethon_api_menu через callback, бо вже відправили повідомлення з клавіатурою.
        # Замість цього, можна просто повернути стан до None, якщо вважається, що flow завершено.
        # Або, якщо потрібно, щоб користувач знову побачив меню, просто відправити його.
        # await show_telethon_api_menu(callback=message, state=state) # Цей рядок може бути видалений або змінений

    except Exception as e:
        logger.error(f"Помилка авторизації за кодом для {phone_number}: {e}", exc_info=True)
        if "session password" in str(e).lower() or isinstance(e, events.RpcCallError) and e.code == 400 and "PASSWORD_REQUIRED" in e.text:
            await message.reply("Потрібен двофакторний пароль. Будь ласка, введіть його:", reply_markup=login_keyboard)
            await state.set_state(TelethonAuthStates.waiting_for_2fa_password)
        else:
            await message.reply(f"Помилка авторизації: {e}. Спробуйте ще раз або перевірте код.", reply_markup=login_keyboard)
            await state.set_state(None)
            if phone_number in telethon_manager.clients:
                await telethon_manager.clients[phone_number].disconnect()
                telethon_manager.clients.pop(phone_number)


@router.message(TelethonAuthStates.waiting_for_2fa_password) 
async def handle_telethon_2fa_password(message: Message, state: FSMContext, telethon_manager, db_pool):
    password = message.text.strip()
    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')

    # <--- ДОДАНО ТУТ: Клавіатура для відповідей
    login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відміна авторизації", callback_data="telethon_cancel_auth")]
    ])

    if not phone_number:
        await message.reply("Сталася помилка. Будь ласка, почніть авторизацію знову.", reply_markup=login_keyboard)
        await state.set_state(None)
        return

    client = telethon_manager.get_client(phone_number)
    if not client:
        await message.reply("Клієнт Telethon не знайдено. Будь ласка, почніть авторизацію знову.", reply_markup=login_keyboard)
        await state.set_state(None)
        return

    try:
        await client.sign_in(password=password)
        await telethon_manager.save_session_to_db(phone_number, client, db_pool)
        
        me = await client.get_me()
        await message.reply(f"✅ Успішно авторизовано клієнта {phone_number} як **{me.first_name}** (ID: {me.id}) з 2FA.", reply_markup=get_telethon_actions_keyboard())
        logger.info(f"Клієнт {phone_number} успішно авторизовано з 2FA як {me.first_name} (ID: {me.id}).")
        await state.set_state(None)
        # Аналогічно, як вище, можна не викликати show_telethon_api_menu через callback
        # await show_telethon_api_menu(callback=message, state=state)

    except Exception as e:
        logger.error(f"Помилка авторизації 2FA для {phone_number}: {e}", exc_info=True)
        await message.reply(f"Помилка 2FA: {e}. Спробуйте ще раз або перевірте пароль.", reply_markup=login_keyboard)
        await state.set_state(None)
        if phone_number in telethon_manager.clients:
            await telethon_manager.clients[phone_number].disconnect()
            telethon_manager.clients.pop(phone_number)