# handlers/admin/__init__.py

from .main_menu import router as admin_main_menu_router
from .user_management import router as user_management_router
from .telethon_operations import router as telethon_operations_router

# За бажанням, можна додати список усіх роутерів для зручного включення у main.py
# наприклад: all_admin_routers = [admin_main_menu_router, user_management_router, telethon_operations_router]