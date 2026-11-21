import secrets

import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_jwt_token(data: dict):
    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_token(token: str = Depends(oauth2_sheme)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
        return payload.get('sub')
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='expired token')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')