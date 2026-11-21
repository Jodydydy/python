from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()

class User(BaseModel):
    username: str
    password: str

USER_DATA = [
    User(**{'username': 'user1', 'password': 'pass1'}),
    User(**{'username': 'user2', 'password': 'pass2'})
]    


def get_user_from_db(username: str) -> User:

    for user in USER_DATA:
        if username == user.username:
            return user

    return None        

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    user = get_user_from_db(credentials.username)

    if user is None or user.password != credentials.password:
        raise HTTPException(headers={'WWW-Authenticate': 'Basic'},
                             status_code=status.HTTP_401_UNAUTHORIZED,
                               detail='Invalid credits')

    return user


@app.get('/login')
async def login(user: User = Depends(auth_user)):
    return {'message': 'You got my secret, welcome'}