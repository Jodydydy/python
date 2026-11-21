from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

class User_Adult(User):
    is_adult: bool    