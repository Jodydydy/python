from fastapi import Depends, FastAPI, HTTPException, status
from models import User
from db_data import get_user
from security import create_jwt, get_user_from_token


app = FastAPI()


@app.post('/login')
async def login(user: User):

    user_db = get_user(user.username)

    if user_db is not None and user_db.password == user.password:
        token = create_jwt({'sub': user.username})

        return {'access_token': token, 'token_type': 'bearer'}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')


@app.get('/protected_resource')
async def get_protected_resouce(username: str = Depends(get_user_from_token)):

    user = get_user(username)
    print(username, user)

    if user:
        return {'message': 'user found'}

    return {'message': 'user not found'}