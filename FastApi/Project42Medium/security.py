import datetime
import secrets
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_jwt(data: Dict):

    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_jwt(data: Dict):

    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_payload(token: str = Depends(oauth2_sheme)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='expired token')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')
