# Telegram Бот з Інтегрованим Штучним Інтелектом

Цей проект є телеграм-ботом, який використовує штучний інтелект для обробки запитів користувачів і генерації відповідей.

## Основна функціональність
- Підтримка інтеграції з Telegram API.
- Використання штучного інтелекту для генерації текстів (модель Gemini).
- Робота з базою даних для збереження даних користувачів.

## Структура проекту
```
│── bot.py              # Запуск бота
│── config.py           # Конфігурація (токен, база даних)
│── database.py         # Підключення до БД, моделі
│── handlers/           # Папка з обробниками команд
│   ├── start.py        # Обробник команди /start
│   ├── user.py         # Інші команди користувача
│── keyboards.py        # Клавіатури
│── middlewares.py      # Middleware (наприклад, логування)
│── services.py         # Бізнес-логіка
│── utils.py            # Допоміжні функції
│── gemini.py           # Підключення до ШІ Gemini у планах
```

## Інструкції з встановлення
1. Клонувати репозиторій:
    ```bash
    git clone https://github.com/navigator2601/test_bot.git
    cd test_bot
    ```
2. Встановити залежності:
    ```bash
    pip install -r requirements.txt
    ```

3. Запустити бота:
    ```bash
    python bot.py
    ```
