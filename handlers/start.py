from aiogram import Router, types
from database import add_user

router = Router()

@router.message(commands=["start"])
async def start_handler(message: types.Message, pool):
    await add_user(pool, message.from_user.id, message.from_user.username,
                   message.from_user.first_name, message.from_user.last_name)
    await message.answer("Привіт! Тебе додано до бази 🎉")

