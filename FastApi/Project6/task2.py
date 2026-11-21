import datetime
import re
from typing import Annotated

from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, Field

app = FastAPI()

pattern = r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"

class CommonHeaders(BaseModel):
    user_agent: str = Field(alias='User-Agent')
    accept_language: str = Field(alias='Accept-Language',
                                 pattern=pattern)
    

@app.get('/headers')
async def get_headers(headers: Annotated[CommonHeaders, Header()]):


    user_agent = headers.user_agent
    accept_language = headers.accept_language

    return {'User-Agent': user_agent, 'Accept-Language': accept_language}


@app.get('/info')
async def info(response: Response, headers: Annotated[CommonHeaders, Header()]):

    data = {'message': 'Добро пожаловать! Ваши заголовки успешно обработаны.','headers': headers} 

    response.headers['X-Server-Time'] = datetime.datetime.now().isoformat()

    return data