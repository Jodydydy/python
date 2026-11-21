
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from databases import Database
from models import Todo, TodoResponse, TodoCompleted, ParamsDep, FilterDep, allowed_sort_fields, sql_filters

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


@app.post("/todos", response_model=TodoResponse, status_code=201)
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
            
    
        return TodoResponse(**task)   
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка при созданиии задачи {str(e)}')


@app.get("/todos/analytics")
async def analyze_tasks(timezone: str = "Europe/Moscow"):

    query = """
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE completed = TRUE) AS completed_count
        FROM todo;
    """

    try:
        result = await database.fetch_one(
            query=query
        )                     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')

    total = result['total']
    completed_count = result['completed_count']
    incomplete_count = total - completed_count
    completed_stats = {"completed_stats": { "true": completed_count, "false": incomplete_count}}


    query = """
            SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 3600) AS avg_hours
            FROM todo 
            WHERE completed = true
            """

    try:
        result = await database.fetch_one(
            query=query
        )                     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')

    avg = {"avg_completion_time_hours": result['avg_hours']}


    query = """
            SELECT
                EXTRACT(DOW FROM created_at AT TIME ZONE :timezone) as dow,
                COUNT(*) as task_count
            FROM todo
            GROUP BY dow
            ORDER BY dow
            """

    try:
        result = await database.fetch_all(
            query=query,
            values={'timezone': timezone}
        )                     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    weekday_distribution = {
    "Monday": 0,
    "Tuesday": 0,
    "Wednesday": 0,
    "Thursday": 0,
    "Friday": 0,
    "Saturday": 0,
    "Sunday": 0
    }   

    for row in result:
        day_number = int(row['dow'])
        task_count = row['task_count']
        weekday_distribution[days[day_number]] = task_count
                         
    return {
        "total": total,
        **completed_stats,
        **avg,
        "weekday_distribution": weekday_distribution
    }


@app.patch('/todos')
async def update_tasks(ids: str, completed: bool):

    id_list = [int(id) for id in ids.split(',')]
    query = """
        UPDATE todo
        SET completed = :completed,
        completed_at = CASE
            WHEN :completed = TRUE THEN CURRENT_TIMESTAMP
            ELSE NULL
        END
        WHERE id = ANY(:id_list)
        RETURNING id
    """

    try:
        result = await database.fetch_all(
            query=query,
            values={'completed': completed, 'id_list': id_list}
        )                     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')

    return { "updated_count": len(result) }



@app.get("/todos/{task_id}", response_model=TodoResponse)
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

    return TodoResponse(**task) 



@app.get("/todos/", response_model=list[TodoResponse])
async def get_task(params: ParamsDep, filters: FilterDep):

    sort_field = params.sort_by.lstrip('-')
    sort_direction = 'DESC' if params.sort_by.startswith('-') else 'ASC'

    if sort_field not in allowed_sort_fields:
        raise HTTPException(status_code=422, detail='Wrong sort parameter')

    values = filters.model_dump(exclude_none=True)
    if 'title_contains' in values:
        values['title_contains'] = f"%{values['title_contains']}%"
    conditions = [sql_filters[key] for key in values]

    where_clause = f'WHERE {' AND '.join(conditions)}' if conditions else ""
    values.update({'limit': params.limit, 'offset': params.offset})


    query = f"""
        SELECT *
        FROM Todo
        {where_clause}
        ORDER BY {allowed_sort_fields[sort_field]} {sort_direction}
        LIMIT :limit
        OFFSET :offset
    """  

    try:
        tasks = await database.fetch_all(
            query=query,
            values=values
        )
            
      
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка получения задачи {str(e)}')


    return [TodoResponse(**task) for task in tasks] 

  

@app.put("/todos/{task_id}", response_model=TodoResponse)
async def update_task(task_id: int, task: TodoCompleted):

    query = """
        UPDATE Todo
        SET title = :title, description = :description, completed = :completed,
        completed_at = CASE
            WHEN :completed = TRUE THEN CURRENT_TIMESTAMP
            ELSE NULL
        END            
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


        return TodoResponse(**result)

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