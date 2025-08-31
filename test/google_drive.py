import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

# Налаштування
json_key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
api_key = 'AIzaSyAK9KXlM232YRWODOiSEMeNcKCMupLqnM0'

# Ідентифікатор папки, куди потрібно завантажити файл (наприклад, 'Тест')
folder_id = '1GoN6CfEx2ZKa9U_x2nvnOvKSoggGfVzF'

# Шлях до файлу, який потрібно завантажити
file_path = '/home/kondiki/Refridex/images/logo.jpg'
file_name = 'logo.jpg'

# Аутентифікація
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, ['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds, developerKey=api_key)
    print("Аутентифікація успішна!")
except Exception as e:
    print(f"Помилка аутентифікації: {e}")
    exit()

def upload_file_to_folder(folder_id, file_path, file_name):
    """Завантажує файл у вказану папку."""
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # Використовуємо MediaFileUpload для завантаження файлу
    media = MediaFileUpload(file_path, resumable=True)
    
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Запуск функції для завантаження фото
try:
    print(f"Завантаження фотографії '{file_name}' в каталог 'Тест'...")
    uploaded_file_id = upload_file_to_folder(folder_id, file_path, file_name)
    print(f"Файл успішно завантажено. Ідентифікатор файлу: {uploaded_file_id}")
except Exception as e:
    print(f"Виникла помилка: {e}")