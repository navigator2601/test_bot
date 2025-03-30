import openai
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def get_ai_response(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=150,
    )
    return response.choices[0].message["content"].strip()