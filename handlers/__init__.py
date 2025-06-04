# handlers/__init__.py

# Експортуємо основні роутери, які вже існують
from .start_handler import router as start_router
from .menu_handler import router as menu_router
from .admin_handler import router as admin_router # Для обробки Inline-кнопок адмін-панелі
# from .reply_keyboard_handler import router as reply_keyboard_router # Цей рядок ВИДАЛЯЄМО!
from .echo_handler import router as echo_router # Завжди останній, обробляє невідомі повідомлення

# --- Місце для майбутніх роутерів ---
# Коли ви створюватимете нові файли хендлерів для кнопок Reply-клавіатури,
# імпортуйте їх тут. Наприклад:

# from .admin_menu_handler import router as admin_menu_router # Для кнопки "⚙️ Адміністрування"
# from .catalog_handler import router as catalog_router         # Для кнопки "📚 Каталог"
# from .reports_handler import router as reports_router         # Для кнопки "🧾 Звіт по роботі"
# from .search_handler import router as search_router           # Для кнопки "🕵️ Пошук"
# ... і так далі для інших кнопок