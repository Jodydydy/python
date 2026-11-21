# main.py
import sys
from uuid import uuid4

from fastapi import FastAPI, Request
import random

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

logger.remove()
logger.add(sys.stdout, serialize=True, level="INFO", backtrace=False, diagnose=False)
logger.add("logs/app.log", rotation="2 MB", retention="10 days", serialize=True, level="ERROR", diagnose=False)

app = FastAPI()

class CustomAppError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)



def log_error(request: Request, exc: Exception, *, status_code: int, request_id: str) -> None:
    logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code
        ).opt(exception=exc).error(
            "Request processing failed"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    status_code = 500
    message = "Internal Server Error"       
    request_id = request.headers.get('X-Request-ID') or uuid4().hex
    log_error(request, exc, status_code=status_code, request_id=request_id)         
    

    return JSONResponse(status_code=status_code, content={
        "status_code": status_code,
        "message": message,
        "request_id": request_id
    })


@app.exception_handler(CustomAppError)
async def custom_exception_handler(request: Request, exc: Exception):

    status_code = exc.code
    message = exc.message

    log_error(request, exc, status_code=status_code)         
    

    return JSONResponse(status_code=status_code, content={
        "status_code": status_code,
        "message": message
    })



@app.get("/ok")
async def ok():
    return {"status": "ok"}

@app.get("/error")
async def error():
    raise CustomAppError("Демонстрационная ошибка", code=418)

# Маршрут для проверки случайного необработанного исключения (ожидается 500)
@app.get("/boom")
async def boom():


    def div_by_zero():
        return 1 / 0

    def key_err():
        return {}["missing"]

    def value_err():
        return int("not-an-int")

    def runtime_err():
        raise RuntimeError("Случайная ошибка")

    random.choice([div_by_zero, key_err, value_err, runtime_err])()
    return {"status": "unreachable"}  # до сюда выполнение не дойдет


