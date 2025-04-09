import os
from google.cloud import aiplatform
from dotenv import load_dotenv

# Завантаження змінних з файлу .env
load_dotenv()

# Зчитування змінних середовища
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
REGION = os.getenv("GOOGLE_LOCATION")
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Перевірка, чи всі необхідні змінні задані
if not PROJECT_ID or not REGION or not SERVICE_ACCOUNT_PATH:
    raise ValueError("Перевірте файл .env. Деякі змінні не задані: GOOGLE_PROJECT_ID, GOOGLE_LOCATION або GOOGLE_APPLICATION_CREDENTIALS.")

# Встановлення облікових даних
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH

# Ініціалізація aiplatform
aiplatform.init(
    project=PROJECT_ID,
    location=REGION
)

# Завантаження моделі та тестовий виклик
try:
    llm = aiplatform.TextGenerationModel.from_pretrained("text-bison")
    prompt = "Привіт! Як справи?"
    response = llm.predict(prompt=prompt)
    print("Відповідь моделі:", response.text)
except Exception as e:
    print(f"Виникла помилка: {e}")