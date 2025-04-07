from aiogram import Router
from aiogram.types import Message
from gemini import generate_gemini_response
from services import save_user
from utils import format_response

router = Router()

@router.message()
async def handle_user_message(message: Message):
    user_query = message.text
    response = generate_gemini_response(user_query)
    if response.startswith("Error:"):
        await message.reply(response)
    else:
        formatted_response = format_response(response)
        await message.reply(formatted_response)
    save_user(message.from_user.username)

def register_handlers_user(dp):
    dp.include_router(router)