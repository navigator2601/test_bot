# Обробник текстових повідомлень
from aiogram import Router, types

# Ініціалізація роутера
router = Router()

# Обробник текстових повідомлень
@router.message()
async def handle_text_messages(message: types.Message):
    pass  # Повідомлення видалено. Обробник нічого не відповідає.

# Функція реєстрації роутера
def register_text_handler(dp):
    dp.include_router(router)