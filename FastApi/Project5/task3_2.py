import time
from typing import Annotated
from fastapi import FastAPI, Cookie, Response, status
from pydantic import BaseModel
from itsdangerous import BadSignature, URLSafeSerializer

app = FastAPI()

SECRET_KEY = 'super_secret-key'

s = URLSafeSerializer(SECRET_KEY, salt='session')

class User(BaseModel):
    username: str
    password: str


fake_db = [User(username='user123', password='password123')]    

def generate_session_cookie(response: Response, username: str) -> str:
    current_time = int(time.time())

    payload = {'username': username, 'timestamp': current_time}

    #dumps превращает dict в строку
    token = s.dumps(payload)

    response.set_cookie(key='session_token', value=token, max_age=300, httponly=True)
    return token

@app.get('/profile')
async def get_user(response: Response, session_token: Annotated[str | None, Cookie()] = None):
    if not session_token:
        return Response(content='{"message": "Invalid session"}', status_code=401, media_type="application/json")

    try:
        #loads сам проверяет подпись и возвращает исходный dict
        payload = s.loads(session_token)

        username = payload['username']
        t = payload['timestamp']

        time_pass = int(time.time()) - t

        if time_pass > 300:
            return Response(content='{"message": "Session expired"}', status_code=401, media_type="application/json")

        elif 180 <= time_pass <= 300:
            generate_session_cookie(response, username)
            return {'user_id': username}
        else:
            return {'user_id': username}

    except BadSignature:
        return Response(content='{"message": "Invalid session"}', status_code=401, media_type="application/json")


@app.get('login')
async def login(response: Response, user: User):

    for u in fake_db:
        if u.username == user.username and u.password == user.password:

            token = generate_session_cookie(response, user.username)

            return {'session_token', token}

    return Response(
        content='{"message": "user not found"}', 
        status_code=status.HTTP_401_UNAUTHORIZED, 
        media_type="application/json"
    )        