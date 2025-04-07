import json
import requests
from config import GEMINI_SERVICE_ACCOUNT

def generate_gemini_response(user_query):
    service_account_info = json.loads(GEMINI_SERVICE_ACCOUNT)
    
    # Формування JWT для аутентифікації
    import jwt
    import time

    iat = time.time()
    exp = iat + 3600
    payload = {
        'iss': service_account_info['client_email'],
        'sub': service_account_info['client_email'],
        'aud': service_account_info['token_uri'],
        'iat': iat,
        'exp': exp
    }
    private_key = service_account_info['private_key']
    assertion = jwt.encode(payload, private_key, algorithm='RS256')
    
    # Отримання токену доступу
    token_response = requests.post(service_account_info['token_uri'], data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion
    })
    
    if token_response.status_code != 200:
        return f"Error: Unable to retrieve access token. Status code: {token_response.status_code}, Response: {token_response.text}"
    
    access_token = token_response.json().get('access_token')
    
    if not access_token:
        return "Error: Access token is missing in the response."

    # Виконання запиту до Google Gemini
    gemini_endpoint = 'https://gemini.googleapis.com/v1/your_endpoint'  # Замість 'your_endpoint' вставте ваш кінцевий пункт Gemini
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(gemini_endpoint, headers=headers, json={
        "query": user_query
    })
    
    if response.status_code == 200:
        return response.json().get('result')
    else:
        return f"Error: {response.status_code} {response.text}"