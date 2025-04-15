# Telegram Bot Project

Цей проект розроблений для інтерактивного використання в Telegram. Бот створений для пошуку інформації, роботи з базою даних та інтеграції з ШІ.

---

## 📂 Структура проекту

```
├── .env                            # Секретні дані
├── .gitignore                      # Ігнорування файлів git
├── config.py                       # Файл конфігурації
├── main.py                         # Головний файл запуску бота
├── README.md                       # Документація проекту
├── requirements.txt                # Список залежностей
├── ai                              # Пакет інтеграції ШІ
│   ├── chat_gpt.py                 # Інтеграція з GPT
│   ├── __init__.py                 # Ініціалізація пакету інтеграції ШІ
├── database/                       # Модуль роботи з базою даних
│   ├── connection.py               # Підключення до бази даних
│   ├── __init__.py                 # Ініціалізація пакету бази даних
│   ├── models.py                   # Опис моделей бази даних
│   ├── queries.py                  # SQL-запити до бази даних
├── handlers/                       # Обробники команд
│   ├── __init__.py                 # Ініціалізація пакету обробників команд
│   ├── menu_handler.py             # Обробник команд меню
│   ├── reply_keyboard_handler.py   # Реакція на натискання кнопок 
│   ├── start_handler.py            # Обробник команд запуску
│   ├── test_handler.py             # Обробник тестування
│   ├── text_handler.py             # Обробник текстових повідомлень
├── keyboards/                      # Клавіатури
│   ├── __init__.py                 # Ініціалізація пакету клавіатур
│   ├── inline_keyboard.py          # Inline клавіатури
│   ├── reply_keyboard.py           # Клавіатури для головного меню
│   ├── test_menu.py                # Меню для тестування
├── logs/                           # Папка для логів
│   ├── bot.log                     # Логи бота
├── static                          # Нормативна документація
│   ├── normative_docs
│   │   ├── some_doc.pdf
├── tests                           
│   ├── __init__.py                 # Ініціалізація тестів
│   ├── test_database.py            # Тести для бази даних
│   ├── test_handlers.py            # Тести для обробників команд
├── utils
│   ├── logger.py                   # Модуль для логування
│   ├── helpers.py                  # Допоміжні функції
│   ├── __init__.py                 # Ініціалізація пакету утиліт
```

---

## 🚀 Функціонал

- **Каталог брендів**: Динамічний список брендів із бази даних.
- **Довідник**: Інформація про різні аспекти роботи з ботом.
- **Інтеграція з ШІ**: Майбутній модуль для пошуку за допомогою штучного інтелекту.
- **Налаштування**: Проста конфігурація бота.
- **Логування**: Детальне логування подій бота із записом у файл (`logs/bot.log`).
- **Головне меню команд**: Автоматичне встановлення меню команд через BotFather:
  - `/start` — Почати роботу з ботом
  - `/help` — Список доступних команд
  - `/info` — Інформація про бота
- **Команда /help**: Показує список доступних команд.
- **Команда /info**: Виводить інформацію про бота та автора.
- **Головне меню з клавіатурою**: Динамічне меню з кнопками:
  - **Каталог**
  - **Довідник**
  - **Пошук**
  - **Допомога** (дублює команду `/help`)
  - Якщо кількість кнопок непарна, остання кнопка займає ширину двох колонок.

---

## 🛠️ Налаштування

1. **Встановлення залежностей**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Налаштування середовища**:
    Створіть файл `.env` у кореневій папці та додайте:
    ```
    BOT_TOKEN=your-telegram-bot-token
    DATABASE_URL=your-postgresql-database-url
    ```

3. **Запуск бота**:
    ```bash
    python main.py
    ```

4. **Логування**:
    - Усі події бота логуються як у консоль, так і у файл `logs/bot.log`.
    - Лог-файл автоматично обмежується розміром 5 МБ і зберігає до 3 резервних копій.
    - Налаштування логування знаходяться у файлі `utils/logger.py`.

5. **Головне меню команд**:
    - Меню автоматично ініціалізується при запуску бота.
    - Команди меню можна змінювати у файлі `handlers/menu_handler.py`.

6. **Головне меню з клавіатурою**:
    - Клавіатура створюється у файлі `keyboards/reply_keyboard.py`.
    - Кнопки відображаються у 2 стовпчики.
    - Якщо кількість кнопок непарна, остання кнопка займає ширину двох колонок.

---

## 📋 Приклад логування

Лог-файл `logs/bot.log` може виглядати так:

```
2025-04-15 11:00:00 - main - INFO - Бот запускається...
2025-04-15 11:01:00 - handlers.start_handler - INFO - Користувач @example запустив команду /start
2025-04-15 11:02:00 - handlers.text_handler - ERROR - Невідома команда від користувача @example
```

---

Сподіваюся, ця документація допоможе легко зрозуміти структуру та функціонал проекту. Якщо виникнуть питання — звертайтеся! 😄