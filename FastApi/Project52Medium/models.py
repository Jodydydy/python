

from datetime import date
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field

allowed_sort_fields = {
    "title": "title",
    "created_at": "created_at",
    "completed": "completed",
    "id": "id"
}

sql_filters = {
    'completed': 'completed = :completed',
    'created_after': 'created_at >= :created_after',
    'created_before': 'created_at <= :created_before',
    'title_contains': 'title ILIKE :title_contains'
}


class Params(BaseModel):

    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = 'created_at'


class Filter(BaseModel):
    completed: bool | None = None
    created_after: date | None = None
    created_before: date | None = None
    title_contains: str | None = None

ParamsDep = Annotated[Params, Depends(Params)]
FilterDep = Annotated[Filter, Depends(Filter)]

class Todo(BaseModel):
    title: str
    description: str

class TodoCompleted(BaseModel):
    title: str
    description: str
    completed: bool    

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: date
    completed_at: date | None