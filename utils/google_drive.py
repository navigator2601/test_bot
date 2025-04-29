# utils/test_google_drive.py
# Тест підключення до Гугл диска
import os  # Імпорт модуля os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Сервісний акаунт
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """
    Підключається до Google Drive API і повертає сервісний об'єкт.
    """
    creds = None
    try:
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise ValueError(f"Помилка під час підключення до Google Drive: {e}")

def list_files(page_size=10):
    """
    Повертає список файлів з Google Drive.
    """
    try:
        service = get_drive_service()
        results = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        return items
    except Exception as e:
        raise ValueError(f"Помилка під час отримання файлів: {e}")