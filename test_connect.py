from dotenv import load_dotenv
import os

load_dotenv()

print("GOOGLE_PROJECT_ID:", os.getenv("GOOGLE_PROJECT_ID"))
print("GOOGLE_LOCATION:", os.getenv("GOOGLE_LOCATION"))
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))