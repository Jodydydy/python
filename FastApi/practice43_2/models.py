# models.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    full_name: str | None = None
    email: EmailStr | None = None
    disabled: bool = False
    roles: list[str]

class UserLogin(BaseModel):
    username: str
    password: str
