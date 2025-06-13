# handlers/admin/telethon_operations.py

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, FloodWaitError, AuthKeyUnregisteredError,
    PhoneCodeExpiredError, PhoneCodeInvalidError,
)
from telethon.tl.functions.channels import JoinChannelRequest # Цей імпорт також може бути видалений, якщо функціонал приєднання не потрібен

# --- ІМПОРТИ КЛАВІАТУР ---
from keyboards.admin_keyboard import (
    get_admin_main_keyboard,
    get_telethon_actions_keyboard,
    # get_telethon_code_retry_keyboard, # Видаляємо, бо не буде авторизації
    get_cancel_keyboard,
)
from keyboards.callback_factories import AdminCallback

# --- ІМПОРТИ З common ---
from common.states import AdminStates
from common.messages import TELETHON_AUTH_MESSAGES

from config import config
from telegram_client_module.telethon_client import TelethonClientManager

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(AdminCallback.filter(F.action == "telethon_auth"))
async def show_telethon_menu(callback: CallbackQuery):
    logger.info(f"Користувач {callback.from_user.id} відкрив меню 'TeleKey · Авторизація API-зв’язку'.")
    await callback.answer()
    await callback.message.edit_text(
        TELETHON_AUTH_MESSAGES["telethon_main_menu"],
        reply_markup=get_telethon_actions_keyboard()
    )

# --- ВИДАЛЕНО: handle_telethon_start_auth ---
# --- ВИДАЛЕНО: process_phone_number ---
# --- ВИДАЛЕНО: resend_telethon_code ---
# --- ВИДАЛЕНО: process_code ---
# --- ВИДАЛЕНО: process_password ---
# --- ВИДАЛЕНО: handle_telethon_cancel_auth ---

@router.callback_query(AdminCallback.filter(F.action == "telethon_check_status"))
async def check_telethon_status(callback: CallbackQuery, telethon_manager: TelethonClientManager):
    logger.info(f"Користувач {callback.from_user.id} натиснув 'Перевірити статус Telethon'.")
    await callback.answer(TELETHON_AUTH_MESSAGES["telethon_checking_status"], show_alert=False)

    all_client_statuses = await telethon_manager.get_all_client_statuses()

    if not all_client_statuses:
        await callback.message.edit_text(
            TELETHON_AUTH_MESSAGES["telethon_no_sessions_found"],
            reply_markup=get_telethon_actions_keyboard()
        )
        return

    status_messages = []
    for client_status in all_client_statuses:
        is_authorized = client_status['authorized']
        info = client_status['info']

        phone_number = info.get('phone', 'N/A')
        user_id = info.get('id', 'N/A')
        first_name = info.get('first_name', 'N/A')
        username = info.get('username', 'Відсутній')

        if is_authorized:
            status_messages.append(
                f"✅ **Telethon клієнт авторизований.**\n"
                f"**ID:** `{user_id}`\n"
                f"**Ім'я:** `{first_name}`\n"
                f"**Юзернейм:** `{username}`\n"
                f"📞 Номер: `{phone_number}`"
            )
        else:
            status_messages.append(
                f"❌ **Telethon клієнт не авторизований.**\n"
                f"📞 Номер: `{phone_number}`\n"
                f"Статус: {info.get('status', 'Невідомо')}"
            )

    response_text = "<b>Поточний статус Telethon-клієнтів:</b>\n\n" + "\n\n".join(status_messages)
    await callback.message.edit_text(
        response_text,
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode="HTML"
    )
    logger.info(f"Статус Telethon-клієнтів відправлено користувачу {callback.from_user.id}.")

@router.callback_query(AdminCallback.filter(F.action == "telethon_delete_session"))
async def handle_telethon_delete_session_menu(callback: CallbackQuery, telethon_manager: TelethonClientManager):
    logger.info(f"Користувач {callback.from_user.id} натиснув 'Видалити сесію 🗑️'.")
    await callback.answer()

    sessions_from_db = await telethon_manager.get_all_sessions_from_db()

    if not sessions_from_db:
        await callback.message.edit_text(
            TELETHON_AUTH_MESSAGES["telethon_no_sessions_to_delete"],
            reply_markup=get_telethon_actions_keyboard()
        )
        return

    buttons = []
    for session in sessions_from_db:
        phone_number = session['phone_number']
        buttons.append([InlineKeyboardButton(text=f"🗑️ {phone_number}", callback_data=AdminCallback(action="delete_specific_session", phone_number=phone_number).pack())])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=AdminCallback(action="telethon_auth").pack())])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        TELETHON_AUTH_MESSAGES["telethon_session_select_delete"],
        reply_markup=keyboard
    )

@router.callback_query(AdminCallback.filter(F.action == "delete_specific_session"))
async def handle_delete_specific_session(callback: CallbackQuery, telethon_manager: TelethonClientManager, callback_data: AdminCallback):
    phone_number = callback_data.phone_number
    logger.info(f"Користувач {callback.from_user.id} намагається видалити сесію для номера {phone_number}.")
    await callback.answer(f"Видаляю сесію для {phone_number}...", show_alert=False)

    try:
        client_to_disconnect = telethon_manager.get_client(phone_number)
        if client_to_disconnect and client_to_disconnect.is_connected():
            await client_to_disconnect.disconnect()
            telethon_manager.clients.pop(phone_number, None)
            logger.info(f"Активний клієнт для {phone_number} відключено та видалено з кешу перед видаленням сесії з БД.")

        await telethon_manager.delete_session(phone_number)
        await callback.message.edit_text(
            TELETHON_AUTH_MESSAGES["session_deleted"].format(phone_number=phone_number),
            reply_markup=get_telethon_actions_keyboard()
        )
        logger.info(f"Сесія для {phone_number} успішно видалена користувачем {callback.from_user.id}.")
    except Exception as e:
        logger.error(f"Помилка видалення сесії для {phone_number} (user {callback.from_user.id}): {e}", exc_info=True)
        await callback.message.edit_text(
            f"Помилка при видаленні сесії для {phone_number}: {e}",
            reply_markup=get_telethon_actions_keyboard()
        )

# НОВІ ХЕНДЛЕРИ ДЛЯ Отримання інфо про користувача
@router.callback_query(AdminCallback.filter(F.action == "telethon_get_user_info"))
async def handle_telethon_get_user_info(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Користувач {callback.from_user.id} натиснув 'Отримати інфо про користувача'.")
    await callback.answer()
    await callback.message.edit_text(
        "Будь ласка, введіть ID користувача або його юзернейм (наприклад, `@username`) для отримання інформації:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_action="get_user_info")

# --- ВИДАЛЕНО: handle_telethon_join_channel ---

@router.message(AdminStates.waiting_for_telethon_input)
async def process_telethon_input(message: Message, state: FSMContext, telethon_manager: TelethonClientManager):
    user_input = message.text.strip()
    user_id = message.from_user.id
    data = await state.get_data()
    telethon_action = data.get("telethon_action")

    if not telethon_action:
        logger.error(f"Користувач {user_id} ввів дані для Telethon, але 'telethon_action' відсутній у стані.")
        await message.answer("Невідомий запит. Будь ласка, оберіть дію з меню TeleKey.",
                             reply_markup=get_telethon_actions_keyboard())
        await state.clear()
        return

    client = await telethon_manager.get_any_active_client()
    if not client:
        await message.answer("Немає активних Telethon-клієнтів для виконання цієї дії. Будь ласка, авторизуйте клієнта.",
                             reply_markup=get_telethon_actions_keyboard())
        await state.clear()
        return
    
    if telethon_action == "get_user_info":
        logger.info(f"Користувач {user_id} ввів '{user_input}' для отримання інформації про користувача.")
        try:
            entity = None
            try:
                entity = await client.get_entity(int(user_input))
            except ValueError:
                entity = await client.get_entity(user_input)

            if not entity:
                await message.answer("Сутність не знайдена за наданим ID або юзернеймом/посиланням.",
                                     reply_markup=get_telethon_actions_keyboard())
                await state.clear()
                return

            info_text = (
                f"<b>Інформація про сутність:</b>\n"
                f"<b>ID:</b> <code>{entity.id}</code>\n"
                f"<b>Тип:</b> {type(entity).__name__}\n"
                f"<b>Ім'я:</b> {getattr(entity, 'first_name', 'N/A')}\n"
                f"<b>Прізвище:</b> {getattr(entity, 'last_name', 'N/A')}\n"
                f"<b>Юзернейм:</b> @{getattr(entity, 'username', 'N/A')}\n"
                f"<b>Бот:</b> {'Так' if getattr(entity, 'bot', False) else 'Ні'}\n"
                f"<b>Аккаунт Telegram Premium:</b> {'Так' if getattr(entity, 'premium', False) else 'Ні'}\n"
                f"<b>Посилання:</b> {getattr(entity, 'url', 'N/A')}"
            )
            await message.answer(info_text, reply_markup=get_telethon_actions_keyboard(), parse_mode="HTML")

        except Exception as e:
            logger.error(f"Помилка при отриманні інформації про сутність для {user_input}: {e}", exc_info=True)
            await message.answer(f"Не вдалося отримати інформацію: {e}", reply_markup=get_telethon_actions_keyboard())
        finally:
            await state.clear()

    # --- ВИДАЛЕНО: elif telethon_action == "join_channel": ---

    else:
        await message.answer("Невідомий запит. Будь ласка, оберіть дію з меню TeleKey.",
                             reply_markup=get_telethon_actions_keyboard())
        await state.clear()