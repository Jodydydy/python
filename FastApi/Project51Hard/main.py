from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_db_connection
import asyncpg

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Todo(BaseModel):
    title: str
    description: str
    user_id: int

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    user_id: int

class TodoNoId(BaseModel):
    title: str
    description: str
    completed: bool
    user_id: int


async def check_user(user_id: int, db: asyncpg.Connection):

    user = await db.fetchrow('''
            SELECT * FROM users WHERE id = $1
        ''', user_id)    

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with this id not found')


@app.post('/todos', response_model=TodoResponse, status_code=201)
async def add_task(task: Todo, db: asyncpg.Connection = Depends(get_db_connection)):


    await check_user(task.user_id, db)


    result = await db.fetchrow('''
        INSERT INTO Todo (title, description, completed, user_id) VALUES ($1, $2, $3, $4)
        RETURNING *
    ''', task.title, task.description, False, task.user_id)

    return TodoResponse(**result)

@app.get('/todos/{id}')
async def get_task(id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    task = await db.fetchrow('''
        SELECT * FROM Todo WHERE id = $1
    ''', id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404, detail='Task not found')

    return TodoResponse(**task)

@app.get('/todos_users/{user_id}')
async def get_user_tasks(user_id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    await check_user(user_id, db)

    result = await db.fetch('''
        SELECT * FROM Todo WHERE user_id = $1
    ''', user_id)

    return result

@app.put('/todos_update/{id}')
async def update_task(id: int, task: TodoNoId, db: asyncpg.Connection = Depends(get_db_connection)):

    await check_user(task.user_id, db)

    updated_task = await db.fetchrow('''
        UPDATE Todo
        SET title = $1, description = $2, completed = $3, user_id = $4
        WHERE id = $5
        RETURNING *
    ''', task.title, task.description, task.completed, task.user_id, id)

    if updated_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')


    return TodoResponse(**updated_task)

@app.put('/todos_users_update/{user_id}')
async def update_user_tasks(user_id: int, task: TodoNoId, db: asyncpg.Connection = Depends(get_db_connection)):

    await check_user(user_id, db)
    await check_user(task.user_id, db)

    result = await db.fetch('''
        UPDATE Todo
        SET title = $1, description = $2, completed = $3, user_id = $4
        WHERE user_id = $5
        RETURNING *
    ''', task.title, task.description, task.completed, task.user_id, user_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')


    return result

@app.delete('/todos_delete/{id}')
async def delete_task(id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    deleted_id = await db.fetchrow('''
        DELETE FROM Todo WHERE id = $1
        RETURNING id
    ''', id)

    if deleted_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    return {'message': 'successfully deleted'}


@app.delete('/todos_users_delete/{user_id}')
async def delete_user_tasks(user_id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    await check_user(user_id, db)

    result = await db.fetch('''
        DELETE FROM Todo WHERE user_id = $1
        RETURNING id
    ''', user_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    return {'message': 'successfully deleted'}


@app.post('/users')
async def create_user(user: User, db: asyncpg.Connection = Depends(get_db_connection)):

    result = await db.fetchrow('''
            INSERT INTO users (username, password) VALUES ($1, $2)
            RETURNING username
        ''', user.username, user.password)

    return {'message': f'user: {result['username']} created'}


@app.delete('/users/{user_id}')
async def delete_use(user_id: int, db: asyncpg.Connection = Depends(get_db_connection)):

    await check_user(user_id, db)

    result = await db.fetchrow('''
        DELETE FROM users WHERE id = $1
        RETURNING id
    ''', user_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    return {"message": "User and associated todos deleted"}