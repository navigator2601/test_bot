# utils/test_google_drive.py
# Тест підключення до Гугл диска
from utils.google_drive import list_files

try:
    print("Перевірка підключення до Google Drive...")
    files = list_files(page_size=5)
    if files:
        print("Файли в Google Drive:")
        for file in files:
            print(f"{file['name']} (ID: {file['id']})")
    else:
        print("Файлів не знайдено.")
except Exception as e:
    print(f"Помилка: {e}")