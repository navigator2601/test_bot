from aiogram import Dispatcher
from .start import router as start_router
from .user import router as user_router  # Імпортуємо обробники з user.py

def register_handlers(dp: Dispatcher):
    dp.include_router(start_router)  # Реєструємо обробники для /start
    dp.include_router(user_router)  # Реєструємо обробники для інших команд