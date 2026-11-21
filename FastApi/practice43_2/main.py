# main.py
from fastapi import FastAPI, Depends, Request, HTTPException
from models import UserLogin, User
from db import USERS_DATA, get_user
from dependencies import get_current_user
from security import create_jwt_token, username_from_request

# rbacx: модели, страж и FastAPI-адаптер
from rbacx import Guard, Subject, Action, Resource, Context
from rbacx.adapters.fastapi import require_access

# специальный класс для загрузки политики из файла + «горячая» подгрузка
from rbacx.policy.loader import FilePolicySource, HotReloader

app = FastAPI()

# 1) Инициализируем Guard без политики, подключаем загрузчик из файла и делаем начальную загрузку
guard = Guard(policy={})
reloader = HotReloader(
    guard,
    FilePolicySource("policy.json"),
    initial_load=True,  # сразу загрузить при старте
)
# Однократная проверка/загрузка на старте (можно заменить на reloader.start(5.0) — фоновая проверка)
reloader.check_and_reload()

# 2) Фабрика сборки окружения для rbacx
def make_env_builder(action_name: str, resource_type: str):
    def build_env(request: Request):
        username = username_from_request(request)
        user_obj = get_user(username)
        roles = user_obj.roles if user_obj else []
        subject = Subject(id=username, roles=roles)
        action = Action(action_name)
        resource = Resource(type=resource_type)
        context = Context()
        return subject, action, resource, context
    return build_env

# 3) Аутентификация (логин)
@app.post("/login")
async def login(user_in: UserLogin):
    for user in USERS_DATA:
        if user["username"] == user_in.username and user["password"] == user_in.password:
            token = create_jwt_token({"sub": user_in.username})
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Неверные учетные данные")

# 4) Маршрут для админов — проверяем доступ через rbacx
@app.get("/admin", dependencies=[
    Depends(require_access(guard, make_env_builder("view_admin", "page")))
])
async def admin_info(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Welcome to the admin page."}

# 5) Маршрут для пользователей — тоже через rbacx
@app.get("/user", dependencies=[
    Depends(require_access(guard, make_env_builder("view_user", "page")))
])
async def user_info(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Welcome to the user page."}

# 6) Просто вернуть текущего пользователя (только аутентификация)
@app.get("/about_me")
async def about_me(current_user: User = Depends(get_current_user)):
    return current_user
