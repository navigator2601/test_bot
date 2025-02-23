#!/bin/bash

# Створення нового SSH-ключа
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Запуск SSH-агента
eval "$(ssh-agent -s)"

# Додавання SSH-ключа до SSH-агента
ssh-add ~/.ssh/id_rsa

# Вивід публічного ключа
cat ~/.ssh/id_rsa.pub