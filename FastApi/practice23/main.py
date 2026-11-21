from fastapi import FastAPI

app = FastAPI()

fake_users = {
    1: {"username": "john_doe", "email": "john@example.com"},
    2: {"username": "jane_smith", "email": "jane@example.com"},
}

#@app.get('/users')
#async def read_users(limit: int = 10):
#    return dict(list(fake_users.items())[:limit])


@app.get('/users')
async def read_users(username: str = None, email: str = None, limit: int = 10):
    filtred_users = fake_users

    if username:
        filtred_users = {key: user for key, user in filtred_users.items() if username.lower() in
                         user['username'].lower()}

    if email:
        filtred_users = {key: user for key, user in filtred_users.items() if email.lower() in
                        user['email'].lower()}    

    return dict(list(filtred_users.items())[:limit])    

@app.get('/user/{user_id}')
async def get_user(user_id: int):
    return fake_users.get(user_id, {'error': 'User not found'})

"""
@app.get('/users')
async def get_all_users():
    return fake_db

@app.get('/users/{user_id}')
async def get_user(user_id: int):
    return {'iser_id': user_id, 'user': fake_db[user_id]}

@app.post('/add_user')
async def add_user(username: str, user_info: str):
    fake_db.append({'username': username, 'user_info': user_info})
    return {'message': 'User added to database'}
"""