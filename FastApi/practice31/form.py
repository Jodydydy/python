from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get('/', response_class=HTMLResponse)
async def get_form():
    with open('practice31/index.html', 'r', encoding='utf-8') as f:
        return f.read()

# дополним main.py
@app.post("/register/")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    password: str = Form(...)
):
    return {
        "username": username, 
        "email": email, 
        "age": age, 
        "password_length": len(password)
    }

