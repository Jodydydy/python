from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_db_connection
import asyncpg

app = FastAPI()

class Todo(BaseModel):
    title: str
    description: str

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

class TodoNoId(BaseModel):
    title: str
    description: str
    completed: bool


@app.post('/todos', response_model=TodoResponse, status_code=201)
async def add_task(task: Todo, db: asyncpg.Connection = Depends(get_db_connection)):

    print(task)
    result = await db.fetchrow('''
        INSERT INTO Todo (title, description, completed) VALUES ($1, $2, $3)
        RETURNING id
    ''', task.title, task.description, False)

    return TodoResponse(id=result['id'],
                         title=task.title,
                         description=task.description,
                         completed=False)

@app.get('/todos/{id}')
async def get_task(id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    task = await db.fetchrow('''
        SELECT * FROM Todo WHERE id = $1
    ''', id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404, detail='Task not found')

    return TodoResponse(**task)

@app.put('/todos_update/{id}')
async def update_task(id: int, task: TodoNoId, db: asyncpg.Connection = Depends(get_db_connection)):

    updated_task = await db.fetchrow('''
        UPDATE Todo
        SET title = $1, description = $2, completed = $3
        WHERE id = $4
        RETURNING *
    ''', task.title, task.description, task.completed, id)

    if updated_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')


    return TodoResponse(**updated_task)

@app.delete('/todos_delete/{id}')
async def delete_task(id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    deleted_id = await db.fetchrow('''
        DELETE FROM Todo WHERE id = $1
        RETURNING id
    ''', id)

    if deleted_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    return {'message': f'successfully deleted'}