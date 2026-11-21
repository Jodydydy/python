import secrets
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, Request, status
from models import User
from db_data import get_user, add_user, add_refresh, get_refresh, remove_token
from security import create_access_jwt, create_refresh_jwt, get_payload

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from passlib.context import CryptContext

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


myctx = CryptContext(schemes=['bcrypt'])
FAKE_HASH = myctx.hash('fake_password')



def auth_user(user: User) -> User:
        
    user_db = get_user(user.username)

    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    db_username = user_db.username
    db_password = user_db.password
      

    is_correct_username = secrets.compare_digest(user.username, db_username)
    is_correct_password = myctx.verify(user.password, db_password)

    if is_correct_username and is_correct_password:
        return user

    raise HTTPException(headers={'WWW-Authenticate': 'Bearer'},
                                         status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail='Authorization failed')


@app.post('/register', status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def register(request: Request, user: User):


    if get_user(user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    password = myctx.hash(user.password)
    add_user(User(username=user.username, password=password))

    return {'message': 'New user created'}


@app.post('/login')
@limiter.limit("5/minute")
async def login(request: Request, user: User):

    auth_user(user)

    access_token = create_access_jwt({'username': user.username, 'type': 'access'})
    refresh_token = create_refresh_jwt({'username': user.username, 'type': 'refresh'})

    add_refresh({user.username: refresh_token})

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@app.post('/refresh')
@limiter.limit("5/minute")
async def refresh(request: Request, token: Dict):

        refresh_token = token.get('refresh_token')
        payload = get_payload(refresh_token)
        username = payload.get('username')

        tokens = get_refresh()

        if tokens.get(username) != refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    

        if payload.get('type') == 'refresh':

            access_token = create_access_jwt({'username': username, 'type': 'access'})
            new_refresh_token = create_refresh_jwt({'username': username, 'type': 'refresh'})

            remove_token(username)
            add_refresh({username: new_refresh_token})

            return {'access_token': access_token, 'refresh_token': new_refresh_token, 'token_type': 'bearer'}


    
        raise HTTPException(headers={'WWW-Authenticate': 'Bearer'},
                                             status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail='Authorization failed')


@app.get('/protected_resource')
async def get_protected_resouce(payload: dict = Depends(get_payload)):

    user = get_user(payload.get('username'))

    if user and payload.get('type') == 'access':
        return {'message': 'Access granted'}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access not granted')