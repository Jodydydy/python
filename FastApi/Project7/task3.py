import secrets
from typing import Annotated

from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from passlib.context import CryptContext
from . import config

setting = config.get_setting()

if setting.mode == 'DEV':    
    app = FastAPI(docs_url=None, openapi_url=None, redoc_url=None)
elif setting.mode == 'PROD':
    app = FastAPI(docs_url=None, openapi_url=None, redoc_url=None)
else:
    raise ValueError("Invalid MODE")  
        
security = HTTPBasic()
myctx = CryptContext(schemes=['md5_crypt'])

class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str    

FAKE_HASH = myctx.hash('fake_password')

fake_users_db = []    


def get_user_from_db(username: str) -> UserInDB:

    for user in fake_users_db:
        if username == user.username:
            return user

    return None        

def auth_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> UserInDB:
    user = get_user_from_db(credentials.username)


    if user is not None:
        db_username = user.username
        db_password = user.hashed_password
        user_exists = True

    else:
        db_username = credentials.username
        db_password = FAKE_HASH
        user_exists = False        

    is_correct_username = secrets.compare_digest(credentials.username, db_username)
    is_correct_password = myctx.verify(credentials.password, db_password)

    if user_exists and is_correct_username and is_correct_password:
        return user

    raise HTTPException(headers={'WWW-Authenticate': 'Basic'},
                                         status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail='Invalid credits')


def auth_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):


    if secrets.compare_digest(setting.mode, "DEV"):
        is_username_correct = secrets.compare_digest(setting.docs_user, credentials.username)
        is_password_correct = secrets.compare_digest(setting.docs_password, credentials.password)

        if is_username_correct and is_password_correct:
            return credentials.username

    elif secrets.compare_digest(setting.mode, "PROD"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')

    raise HTTPException(headers={'WWW-Authenticate': 'Basic'},
                                             status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail='Invalid MODE')



if setting.mode == 'DEV':

    @app.get('/openapi.json', include_in_schema=False)
    async def open_api(username: str = Depends(auth_admin)):
        return app.openapi()

    @app.get('/docs', include_in_schema=False)
    async def docs(username: str = Depends(auth_admin)):
        return get_swagger_ui_html(openapi_url='/openapi.json',
                                   title=app.title + " - Swagger UI")


    
@app.post('/register')
async def register(user: User):
    password = myctx.hash(user.password)
    fake_users_db.append(UserInDB(username=user.username, hashed_password=password))

    return {'message': 'User successfully registered'}

@app.get('/login')
async def login(user: UserInDB = Depends(auth_user)):
    return {'message': f'Welcome, {user.username}!'}