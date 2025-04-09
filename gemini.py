# Підключення до ШІ Gemini
import requests
import logging

class GeminiAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.gemini.com/v1/"

    def generate_response(self, prompt):
        logging.info(f"Sending request to Gemini AI with prompt: {prompt}")
        response = requests.post(
            f"{self.base_url}generate",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt, "additional_param": "value"}  # Додайте додаткові параметри, якщо необхідно
        )
        logging.info(f"Received response from Gemini AI: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return response.json().get("response")
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

# Приклад використання
if __name__ == "__main__":
    api_key = "your-gemini-api-key"
    gemini_ai = GeminiAI(api_key)
    print(gemini_ai.generate_response("Hello, Gemini!"))