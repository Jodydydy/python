import datetime
import secrets
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Request, status

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = secrets.token_hex(32) 
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_jwt_token(data: dict) -> str:

    to_encode = data.copy()

    exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': exp})

    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

def decode_token(token: str) -> str:

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get('sub')

        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid token')
        return username
    except jwt.ExpiredSignatureError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='Token expired')
    except jwt.InvalidTokenError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='Invalid token')


def get_user_from_token(token: str = Depends(oauth2_sheme)):
    return decode_token(token) 

def username_from_request(request: Request) -> str:
    auth = request.headers.get('authorization', "")
    prefix = "bearer "

    if not auth.lower().startswith(prefix):
        return 'anon'
    token = auth[len(prefix):].strip()

    try:
        return decode_token(token)
    except HTTPException:
        return 'anon'   