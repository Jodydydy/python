from typing import Annotated
import uuid
from fastapi import FastAPI, Cookie, HTTPException, Response, status
from pydantic import BaseModel
from itsdangerous import BadSignature, Signer, base64_decode, base64_encode


app = FastAPI()

class User(BaseModel):
    username: str
    password: str

fake_db = [User(username='user123', password='password123')]    
fake_db_session_token = []


@app.post('/login')
async def login(response: Response, user: User):
    token = None

    for u in fake_db:
        if u.username == user.username:
            if u.password == user.password:
                user_id = str(uuid.uuid4()) 
                s = Signer('secret-key', key_derivation='hmac')
                token_bytes = s.sign(user_id.encode('utf-8'))
                token = token_bytes.decode('utf-8')
                fake_db_session_token.append({'username': user.username, 'session_token': token})
                response.set_cookie(key='session_token', value=token, max_age=3600, httponly=True)
                break


    if token is not None:
        return {'session_token': token}
    else:
        return Response(content='{"message": "user not found"}', status_code=401, media_type="application/json")

@app.get('/profile')
async def get_user(session_token: Annotated[str | None, Cookie()] = None):

    if session_token is not None:
        s = Signer('secret-key', key_derivation='hmac')

        try:
            verif_bytes = s.unsign(session_token.encode('utf-8'))
            user_id = verif_bytes.decode('utf-8')
            return {'user_id': user_id}
        except BadSignature:
            pass      


        
    return Response(content='{"message": "Unauthorized"}', status_code=401, media_type="application/json")  