# Heroku Commands

## Логін

Увійдіть у свій обліковий запис Heroku:
```bash
heroku login
```

## Перегляд динамічних ресурсів додатка

Перевірте стан вашого додатка:
```bash
heroku ps -a kondiki
```

## Перегляд журналів додатка

Перегляньте журнали вашого додатка:
```bash
heroku logs -a kondiki --tail
```

## Перегляд конфігураційних змінних

Перевірте конфігураційні змінні вашого додатка:
```bash
heroku config -a kondiki
```

## Інформація про додаток

Перевірте інформацію про додаток:
```bash
heroku info -a kondiki
```

## Створення нового додатка

Створіть новий додаток на Heroku:
```bash
heroku create your-app-name
```

## Розгортання додатка

Розгорніть додаток вручну:
```bash
heroku git:remote -a kondiki
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```