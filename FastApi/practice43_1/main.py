from fastapi import FastAPI, Depends, HTTPException, status
from security import create_jwt_token
from models import UserLogin, User
from db import USERS_DATA
from dependencies import get_current_user
from rbac import PermissionChecker

app = FastAPI()

@app.post('/login')
async def login(user_in: UserLogin):

    for user in USERS_DATA:
        if user['username'] == user_in.username and user['password'] == user_in.password:

            token = create_jwt_token({'sub': user_in.username})
            return {'access_token': token, 'token_type': 'bearer'}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверные учетные данные')     


@app.get('/admin')
@PermissionChecker(["admin"])
async def admin_info(current_user: User = Depends(get_current_user)):
    return {'message': f'Hello, {current_user.username}. Welcome to admin page'}

@app.get('/user')
@PermissionChecker(['user'])
async def user_info(current_user: User = Depends(get_current_user)):
    return {'message': f'Hello, {current_user.username}. Welcome to user page'}


@app.get('/about_me')
async def about_me(current_user: User = Depends(get_current_user)):
    return current_user