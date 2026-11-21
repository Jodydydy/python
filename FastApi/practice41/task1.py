from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()

#модель пользователя
class User(BaseModel):
    username: str
    password: str

USER_DATA = [
    User(**{'username': 'user1', 'password': 'pass1'}),
    User(**{'username': 'user2', 'password': 'pass2'})
]    

def get_user_from_db(username: str) -> User:
    for user in USER_DATA:
        if user.username == username:
            return user

    return None        

#функция аутентификации
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    user = get_user_from_db(credentials.username)

    if user is None or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    return user


@app.get('/protected_resource/')
async def get_protected_resource(user: User = Depends(authenticate_user)):
    return {'message': 'You have acess to the protected resources', 'user_info': user}