# handlers/__init__.py

# Експортуємо основні роутери
from .start_handler import router as start_router
from .menu_handler import router as menu_router

# <--- ОНОВЛЕНІ ІМПОРТИ: Тепер імпортуємо з нової структури адмін-панелі --->
from .admin.main_menu import router as admin_main_menu_router
from .admin.user_management import router as user_management_router
from .admin.telethon_operations import router as telethon_operations_router
# <-------------------------------------------------------------------------->

# from .admin_handler import router as admin_router # Цей рядок ВИДАЛЯЄМО!
# from .reply_keyboard_handler import router as reply_keyboard_router # Цей рядок ВИДАЛЯЄМО!
from .echo_handler import router as echo_router # Завжди останній, обробляє невідомі повідомлення

# --- Місце для майбутніх роутерів ---
# Коли ви створюватимете нові файли хендлерів для кнопок Reply-клавіатури,
# імпортуйте їх тут. Наприклад:

# from .catalog_handler import router as catalog_router
# from .reports_handler import router as reports_router
# from .search_handler import router as search_router
# ... і так далі для інших кнопок