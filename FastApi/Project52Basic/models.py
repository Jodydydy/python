

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(BaseModel):
    pass

class UserReturn(UserBase):
    id: int

class Todo(BaseModel):
    title: str
    description: str

class TodoCompleted(BaseModel):
    title: str
    description: str
    completed: bool    

class TodoResponce(BaseModel):
    id: int
    title: str
    description: str
    completed: bool