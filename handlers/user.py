from aiogram import types
from aiogram.dispatcher import Dispatcher
from openai_utils import generate_response
from services import save_user
from utils import format_response

async def handle_user_message(message: types.Message):
    user_query = message.text
    response = generate_response(user_query)
    formatted_response = format_response(response)
    await message.reply(formatted_response)
    save_user(message.from_user.username)

def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(handle_user_message, content_types=types.ContentType.TEXT)