from typing import Dict

from models import User

USER_DATA = []
refresh_tokens = dict()

def get_user(username: str) -> User:

    for user in USER_DATA:
        if user.username == username:
            return user

    return None        

def add_user(user: User):
    USER_DATA.append(user)

def add_refresh(token: Dict):

    refresh_tokens.update(token)

def get_refresh():

    return refresh_tokens.copy()

def remove_token(username: str):
    refresh_tokens.pop(username)