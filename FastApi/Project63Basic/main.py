from random import randint

from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import User, ProblemDetails, UserResponse


app = FastAPI()

FAKE_BD = [{'id': 1, 'user': User(username='admin', password='pass1')}]

problem_example = {
    "type": "https://example.com/problems/validation-error",
    "title": "Validation Error",
    "status": 422,
    "detail": "The request body failed validation.",
    "instance": "/users",
    "errors": [
        {
            "field": "username",
            "message": "field required",
            "code": "value_error.missing",
        }
    ],
}


@app.exception_handler(RequestValidationError)
async def validation_exeception_handler(requset: Request, exc: RequestValidationError):

    errors = [{"field": error['loc'][1] if len(error['loc']) > 1 else None,
                "message": error["msg"],
                  "code": error["type"]} for error in exc.errors()]

    instance = requset.url.path


    content = ProblemDetails(type=f"https://example.com/problems/validation-error",
                   title="Validation Error",
                   status=422,
                   detail="The request body failed validation.",
                   instance=instance,
                   errors=errors)

    return JSONResponse(status_code=422,
                        headers={'Content-Type': 'application/problem+json'},
                        content=jsonable_encoder(content))

@app.post('/register')
async def create_user(user: User):
    FAKE_BD.append({"id": randint(2, 1000)})
    return UserResponse(id=randint(1, 1000), username=user.username)

