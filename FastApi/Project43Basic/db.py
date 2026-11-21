# db.py
from models import User

USERS_DATA = [
    {
        "username": "admin",
        "password": "adminpass",
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False
    },
    {
        "username": "user",
        "password": "userpass",
        "roles": ["user"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False
    },
    {
        "username": "guest",
        "password": "guestpass",
        "roles": ["guest"],
        "full_name": "Regular guest",
        "email": "guest@example.com",
        "disabled": False
    },
    {
        "username": "guest2",
        "password": "guestpass2",
        "roles": ["guest"],
        "full_name": "Regular guest2",
        "email": "guest2@example.com",
        "disabled": False
    }    
]

POSTS = []

resources = {  
    "alice": {"content": "Секретные данные Алисы", "is_public": False},  
    "bob": {"content": "Публичные заметки Боба", "is_public": True},  
    "admin": {"content": "Админский ресурс", "is_public": False}  
}  


def get_user(username: str) -> User | None:
    for user_data in USERS_DATA:
        if user_data["username"] == username:
            return User(**{k: v for k, v in user_data.items() if k != "password"})
    return None
