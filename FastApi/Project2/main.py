from fastapi import FastAPI
from user_model import User, User_Adult

app = FastAPI()

def user_is_old(age: int):
    return age >= 18

@app.post('/user', response_model=User_Adult)
async def root(user: User):
    is_adult = user_is_old(user.age)

    item_dict = user.model_dump()

    return item_dict | {'is_adult': is_adult}