import os
import requests, uuid
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_AUTH = os.getenv("GIGACHAT_AUTH")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE")
GIGACHAT_TOKEN_URL = os.getenv("GIGACHAT_TOKEN_URL")
GIGACHAT_API_URL = os.getenv("GIGACHAT_API_URL")
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
GIGACHAT_MODEL = "GigaChat-2-Max"

def get_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_AUTH}'
    }
    data = f'scope={GIGACHAT_SCOPE}'
    response = requests.post(GIGACHAT_TOKEN_URL, headers=headers, data=data, verify=False)

    return response.json()['access_token']


def generate_response(messages: list) -> str:
    token = get_token()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload ={
        "model": GIGACHAT_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 512,
        "stream": False
    }

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)
    return response.json()['choices'][0]['message']['content']