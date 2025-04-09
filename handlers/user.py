from aiogram import Router
from aiogram.types import Message
from predict import predict_text
from services import save_user
from utils import format_response

router = Router()

@router.message()
async def handle_user_message(message: Message):
    user_query = message.text
    try:
        response = predict_text(user_query)
        formatted_response = format_response(response)
        await message.reply(formatted_response)
    except Exception as e:
        await message.reply(f"Error occurred: {e}")
    save_user(message.from_user.username)

def register_handlers_user(dp):
    dp.include_router(router)