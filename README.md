![Логотип проекту](images/logo.jpg)

Цей проєкт розроблений для інтерактивного використання в Telegram. Бот створений для пошуку інформації, роботи з базами даних, інтеграції зі штучним інтелектом та взаємодії з користувачем через зручні меню.

---

## 📂 Структура проєкту

```
.
├── common
│   ├── constants.py
│   ├── __init__.py
│   ├── messages.py
│   └── states.py
├── config.py
├── database
│   ├── db_pool_manager.py
│   ├── __init__.py
│   ├── telethon_chats_db.py
│   ├── telethon_sessions_db.py
│   └── users_db.py
├── filters
│   └── admin_filter.py
├── handlers
│   ├── admin
│   │   ├── chat_matrix_handlers.py
│   │   ├── __init__.py
│   │   ├── main_menu.py
│   │   ├── telethon_operations.py
│   │   └── user_management.py
│   ├── echo_handler.py
│   ├── __init__.py
│   ├── menu_handler.py
│   └── start_handler.py
├── images
│   ├── baner.png
│   └── logo.jpg
├── __init__.py
├── keyboards
│   ├── admin_keyboard.py
│   ├── callback_factories.py
│   ├── __init__.py
│   ├── inline_keyboard.py
│   └── reply_keyboard.py
├── main.py
├── middlewares
│   ├── db_middleware.py
│   ├── dependencies.py
│   ├── exception_middleware.py
│   ├── __init__.py
│   └── telethon_middleware.py
├── README.md
├── requirements.txt
├── states
│   ├── admin_states.py
│   └── __init__.py
├── telegram_client_module
│   ├── auth_telethon.py
│   ├── __init__.py
│   └── telethon_client.py
└── utils
    ├── auth_check.py
    ├── __init__.py
    ├── logger.py
    └── set_bot_commands.py
```
