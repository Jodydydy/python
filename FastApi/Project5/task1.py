from typing import Annotated
import uuid
from fastapi import FastAPI, Cookie, HTTPException, Response, status
from pydantic import BaseModel


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
                token = str(uuid.uuid4()) 
                fake_db_session_token.append({'username': user.username, 'session_token': token})
                response.set_cookie(key='session_token', value=token, httponly=True)
                break


    if token is not None:
        return {'session_token': token}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'message': 'user not found'}

@app.get('/user')
async def get_user(session_token: Annotated[str | None, Cookie()] = None):

    for user in fake_db_session_token:
        print(user['session_token'])
        if user['session_token'] == session_token:

            return {'username': user['username']}

    raise HTTPException(status_code=401, detail='Unauthorized')
        
