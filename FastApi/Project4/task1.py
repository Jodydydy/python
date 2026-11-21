from fastapi import FastAPI
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str
    email: str = Field(pattern=r"[^@]+@[^@]+\.[^@]+", description="Incorrect email")
    age: int = Field(default=None, gt=0, lt=120)
    is_subscribed: bool | None = None

app = FastAPI()


@app.post('/create_user')
async def create_user(user: UserCreate):
    return user