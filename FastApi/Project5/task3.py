from typing import Annotated
import uuid
import time
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
from itsdangerous import BadSignature, Signer


app = FastAPI()

class User(BaseModel):
    username: str
    password: str

fake_db = [User(username='user123', password='password123')]    
fake_db_session_token = []

def generate_cookie(response: Response, user: User):
    s = Signer('secret-key', key_derivation='hmac')
    
    data_to_sign = f'{str(uuid.uuid4())}.{int(time.time())}'
    
    token_bytes = s.sign(data_to_sign.encode('utf-8'))
    token = token_bytes.decode('utf-8')
    fake_db_session_token.append({'username': user.username, 'session_token': token})
    response.set_cookie(key='session_token', value=token, max_age=300, httponly=True, secure=False)

    return token

def find_user(token: str):

    user_name = None

    for u in fake_db_session_token:
        if u['session_token'] == token:
            user_name = u['username']

    for user in fake_db:
        if user.username == user_name:
            return user

    return None                

@app.post('/login')
async def login(response: Response, user: User):
    token = None

    for u in fake_db:
        if u.username == user.username:
            if u.password == user.password:

                token = generate_cookie(response, user)
                break


    if token is not None:
        return {'session_token': token}
    else:
        return Response(content='{"message": "user not found"}', status_code=401, media_type="application/json")

@app.get('/profile')
async def get_user(response: Response, session_token: Annotated[str | None, Cookie()] = None):

    if session_token is not None:
        s = Signer('secret-key', key_derivation='hmac')

        try:
            verif_bytes = s.unsign(session_token.encode('utf-8'))
            user_id, t = tuple(verif_bytes.decode('utf-8').split('.'))
            user = find_user(session_token)

            time_pass = time.time() - int(t)

            if time_pass > 300:
                return Response(content='{"message": "Session expired"}', status_code=401, media_type="application/json")

            elif 300 >= time_pass >= 180:
                if user is not None:
                    generate_cookie(response, user)
                return {"user_id": user_id}

            else:
                return {'user_id': user_id}
        except BadSignature:
            pass      


        
    return Response(content='{"message": "Invalid session"}', status_code=401, media_type="application/json")  