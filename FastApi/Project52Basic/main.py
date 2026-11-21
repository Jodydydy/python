from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from databases import Database
from models import Todo, TodoResponce, UserBase, UserReturn, UserCreate, TodoCompleted

DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydatabase"

database = Database(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):

    """
    Контекстный менеджер для управления подключением к БД.
    Заменяет устаревшие @app.on_event("startup") и @app.on_event("shutdown")
    """
    await database.connect()
    yield
    await database.disconnect() 


app = FastAPI(lifespan=lifespan)


#Создание пользователя
@app.post("/users/", response_model=UserReturn)
async def create_user(user: UserCreate):

    # SQL-запрос с параметризацией (защита от SQL-инъекций)
    query = """
        INSERT INTO users (username, email)
        VALUES (:username, :email)
        RETURNING id  /* Получаем автоматически сгенерированный ID */
    """

    try:
        user_id = await database.execute(
            query=query,
            values=user.model_dump()
        )

        return UserReturn(
            id=user_id,
            **user.model_dump()
        )   

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка при созданиии пользователя {str(e)}')



# Эндпоинт для получения пользователя по ID
@app.get("/users/{user_id}", response_model=UserReturn)
async def get_user(user_id: int):
    """
    Получение информации о пользователе по его ID.
    
    Параметры:
    - user_id: идентификатор пользователя в БД
    
    Возвращает:
    - Данные пользователя в формате UserReturn
    - 404 ошибку если пользователь не найден
    """
    query = """
        SELECT id, username, email 
        FROM users 
        WHERE id = :user_id
    """
    try:
        result = await database.fetch_one(
            query=query,
            values={"user_id": user_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения пользователя: {str(e)}"
        )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Пользователь с указанным ID не найден"
        )

    return UserReturn(
        id=result["id"],
        username=result["username"],
        email=result["email"]
    )    


# Роут для полного обновления информации о пользователе по ID
@app.put("/users/{user_id}", response_model=UserReturn)
async def update_user(user_id: int, user: UserCreate):
    """
    Полное обновление данных пользователя по ID (PUT-запрос).

    Параметры:
    - user_id: ID пользователя в базе данных
    - user: новые данные пользователя (все поля обязательны)

    Возвращает:
    - Обновленные данные пользователя в формате UserReturn
    - 404 ошибку если пользователь не найден
    - 500 ошибку при проблемах с базой данных

    Пример запроса:
    {
        "username": "new_username",
        "email": "new_email@example.com"
    }
    """
    # SQL-запрос с возвратом обновленных данных
    query = """
        UPDATE users
        SET username = :username, email = :email
        WHERE id = :user_id
        RETURNING id
    """

    values = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email
    }

    try:
        # Выполняем запрос и получаем обновленные данные
        result = await database.execute(query=query, values=values)

        # Если запись не найдена
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Пользователь с указанным ID не найден"
            )

        # Преобразуем результат запроса в модель UserReturn
        return UserReturn(**user.model_dump(), id=result,)

    except HTTPException as he:
        # Пробрасываем HTTPException из проверки выше
        raise 

    except Exception as e:
        # Обрабатываем другие ошибки базы данных
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления пользователя: {str(e)}"
        )


# Роут для удаления пользователя по ID
@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    """
    Удаление пользователя из базы данных по ID.

    Параметры:
    - user_id: идентификатор пользователя для удаления

    Возвращает:
    - Сообщение об успешном удалении
    - 404 ошибку если пользователь не найден
    - 500 ошибку при проблемах с базой данных
    """
    query = """
        DELETE FROM users 
        WHERE id = :user_id
        RETURNING id
    """
    try:
        # Пытаемся удалить запись и получить подтверждение
        deleted_id = await database.execute(
            query=query,
            values={"user_id": user_id}
        )
        
        if not deleted_id:
            raise HTTPException(
                status_code=404,
                detail="Пользователь с указанным ID не найден"
            )
            
        return {"message": "Пользователь успешно удален"}
        
    except HTTPException as he:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления пользователя: {str(e)}"
        )    


@app.post("/todos", response_model=TodoResponce, status_code=201)
async def create_task(task: Todo):

    query = """
        INSERT INTO Todo (title, description)
        VALUES (:title, :description)
        RETURNING *
    """  

    try:
        task = await database.fetch_one(
            query=query,
            values=task.model_dump()
        )
            
    
        return TodoResponce(**task)   
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка при созданиии задачи {str(e)}')

@app.get("/todos/{task_id}", response_model=TodoResponce)
async def get_task(task_id: int):

    query = """
        SELECT *
        FROM Todo
        WHERE id = :task_id
    """  

    try:
        task = await database.fetch_one(
            query=query,
            values={'task_id': task_id}
        )
            
      
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Задача с указанным ID не найден"
        )

    return TodoResponce(**task) 


@app.put("/todos/{task_id}", response_model=TodoResponce)
async def update_task(task_id: int, task: TodoCompleted):

    query = """
        UPDATE Todo
        SET title = :title, description = :description, completed = :completed
        WHERE id = :task_id
        RETURNING *
    """

    values = {
        "task_id": task_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed
    }

    try:
        result = await database.fetch_one(query=query, values=values)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Задача с указанным ID не найден"
            )


        return TodoResponce(**result)

    except HTTPException as he:
        raise 

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления задачи: {str(e)}"
        )


@app.delete("/todos/{task_id}", response_model=dict)
async def delete_task(task_id: int):

    query = """
        DELETE FROM Todo 
        WHERE id = :task_id
        RETURNING id
    """
    try:
        deleted_id = await database.fetch_one(
            query=query,
            values={"task_id": task_id}
        )
        
        if not deleted_id:
            raise HTTPException(
                status_code=404,
                detail="Задача с указанным ID не найден"
            )
            
        return {"message": "Задача успешно удалена"}
        
    except HTTPException as he:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления задачи: {str(e)}"
        )        