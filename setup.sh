#!/bin/bash

# Створення файлу Procfile
cat <<EOL > Procfile
web: python bot_menu.py
EOL

# Створення файлу requirements.txt
cat <<EOL > requirements.txt
Flask==2.0.2
gunicorn==20.1.0
python-telegram-bot==13.7
asyncpg==0.30.0
EOL

# Створення файлу README.md
cat <<EOL > README.md
# My Heroku App

## Опис

Цей проект демонструє, як зв'язати Heroku з репозиторієм GitHub і автоматично розгортати додаток.

## Налаштування

1. Встановіть [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. Логіньтесь до Heroku через CLI:
   \`\`\`bash
   heroku login
   \`\`\`
3. Створіть новий додаток на Heroku:
   \`\`\`bash
   heroku create your-app-name
   \`\`\`
4. Відкрийте [Dashboard Heroku](https://dashboard.heroku.com/apps) у вашому браузері.
5. Виберіть ваш додаток.
6. Перейдіть на вкладку "Deploy".
7. У секції "Deployment method" оберіть "GitHub".
8. Натисніть "Connect to GitHub".
9. Введіть свої облікові дані GitHub та авторизуйте Heroku для доступу до ваших репозиторіїв.
10. Оберіть ваш репозиторій зі списку та натисніть "Connect".

## Деплоювання

### Автоматичне деплоювання

1. Увімкніть автоматичне деплоювання у секції "Automatic deploys".
2. Ваш додаток буде автоматично розгортатися щоразу, коли новий код буде злитий у вибрану гілку GitHub.

### Ручне деплоювання

1. Ви також можете вручну розгорнути додаток, натиснувши кнопку "Deploy Branch" у секції "Manual deploy".

## Procfile

\`\`\`plaintext
web: python bot_menu.py
\`\`\`

## requirements.txt

\`\`\`plaintext
Flask==2.0.2
gunicorn==20.1.0
python-telegram-bot==13.7
asyncpg==0.30.0
\`\`\`
EOL

echo "Файли створені успішно!"
