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
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
STREAM = os.getenv("STREAM") == "true"
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
