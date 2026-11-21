# security.py
import datetime
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# В проде храните секрет в .env/секрет-хранилище
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    """Возвращает username из токена (клейм `sub`)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Неверный токен")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен устарел")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ошибка авторизации")

def get_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """DI-обёртка под FastAPI (используем в dependencies.py)."""
    return decode_token(token)

def username_from_request(request: Request) -> str:
    """Для rbacx: достаём Bearer-токен вручную и возвращаем subject.id."""
    auth = request.headers.get("authorization", "")
    prefix = "bearer "
    if not auth.lower().startswith(prefix):
        return "anonymous"
    token = auth[len(prefix):].strip()
    try:
        return decode_token(token)
    except HTTPException:
        return "anonymous"
