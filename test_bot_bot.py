import requests
from config import API_KEY, DATABASE_URL, WEBHOOK_URL

class Bot:
    def __init__(self):
        self.api_key = API_KEY
        self.database_url = DATABASE_URL
        self.webhook_url = WEBHOOK_URL

    def run(self):
        print("Bot is running with the following settings:")
        print(f"API Key: {self.api_key}")
        print(f"Database URL: {self.database_url}")
        print(f"Webhook URL: {self.webhook_url}")