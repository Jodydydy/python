from random import randint

from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import User, ProblemDetails, UserResponse


app = FastAPI()

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

@app.post('/users', response_model=UserResponse, responses={422:{
    'model': ProblemDetails,
    'content':{
        'application/problem+json': {
            'examples': {
                'validation_error': {'value': problem_example}
            }
        }
    }
    },
    200: {
    "content": {
        "application/json": {
            "examples": {
                "user_created": {
                    "value": {"id": 1, "username": "alice"}
                }
            }
        }
    }
},})
async def create_user(user: User):

    return UserResponse(id=randint(1, 1000), username=user.username)


original_openapi = app.openapi

def custom_openapi():
    schema = original_openapi()
    content = schema["paths"]["/users"]["post"]["responses"]["422"]["content"]

    generated = content.pop("application/json", None)
    if generated is not None:
        content["application/problem+json"]["schema"] = generated["schema"]

    return schema

app.openapi = custom_openapi