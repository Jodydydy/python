from models import User

USER_DATA = [
    User(username='admin', password='adminpass'),
    User(username='admin2', password='adminpass')
]

def get_user(username: str) -> User:

    for user in USER_DATA:
        if user.username == username:
            return user

    return None        