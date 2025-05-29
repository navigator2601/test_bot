# handlers/echo_handler.py
from aiogram import Router, types
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message()
async def echo_all_messages(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Отримано некомандне повідомлення від {user_name} (ID: {user_id}): {message.text}")
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Не можу скопіювати це повідомлення.")