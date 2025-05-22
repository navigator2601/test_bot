# handlers/__init__.py
from aiogram import Dispatcher

# Імпортуємо всі роутери безпосередньо, а не як модулі
from .start_handler import router as start_router
from .reply_keyboard_handler import router as reply_keyboard_router
from .admin_handler import router as admin_router # <--- Явний імпорт роутера

def register_all_handlers(dp: Dispatcher):
    # Реєструємо роутери
    dp.include_router(start_router)
    dp.include_router(reply_keyboard_router)
    dp.include_router(admin_router) # <--- Реєстрація роутера
    # Додайте тут інші роутери, якщо вони є