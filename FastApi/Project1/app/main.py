from fastapi import FastAPI
from models.models import User

from logger.logger import logger

user: User = User(name="John Doe", id=1)

app = FastAPI()


#@app.post("/post")
#async def post(user: User):
#    print(f"Получили от {user.username} сообщение: {user.message}")
#
#    return user


@app.get("/")
async def root():
    logger.info("Handling request to root endpoint")
    return {"message": "Hello world"}

@app.get('/users')
async def get_users():
    return user


@app.get("/custom")
async def custom_message():
    return {"message": "Custom message"}
