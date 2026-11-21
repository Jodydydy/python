from typing import Optional

from pydantic import BaseModel, EmailStr, conint, constr


class User(BaseModel):

    username: str
    password: constr(min_length=8, max_length=16)


class UserResponse(BaseModel):
    id: int
    username: str

class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: Optional[list]