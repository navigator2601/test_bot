from aiogram import Router, types

# Ініціалізація роутера
router = Router()

# Обробник текстових повідомлень
@router.message()
async def handle_text_messages(message: types.Message):
    await message.reply("ШІ інтелект на етапі розробки, скористайтеся меню або командами бота!")

# Функція реєстрації роутера
def register_text_handler(dp):
    dp.include_router(router)