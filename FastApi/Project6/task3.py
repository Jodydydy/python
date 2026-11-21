import datetime
from typing import Annotated

from fastapi import FastAPI, Header, Response
from pydantic import BaseModel, Field, field_validator

MINIMUM_APP_VERSION = "0.0.2"

app = FastAPI()

pattern = r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"

class CommonHeaders(BaseModel):
    x_current_version: str = Field(alias='X-Current-Version',
                                   pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    user_agent: str = Field(alias='User-Agent')
    accept_language: str = Field(alias='Accept-Language',
                                 pattern=pattern)


    @field_validator('x_current_version')
    @classmethod
    def validate_version(cls, version):

        v = [int(x) for x in version.split('.')]
        min_v = [int(x) for x in MINIMUM_APP_VERSION.split('.')]


        if (min_v > v):
            raise ValueError("Требуется обновить приложение")

        return version

@app.get('/headers')
async def get_headers(headers: Annotated[CommonHeaders, Header()]):


    user_agent = headers.user_agent
    accept_language = headers.accept_language

    return {'User-Agent': user_agent, 'Accept-Language': accept_language}


@app.get('/info')
async def info(response: Response, headers: Annotated[CommonHeaders, Header()]):

    print(headers.x_current_version)

    data = {'message': 'Добро пожаловать! Ваши заголовки успешно обработаны.','headers': headers} 

    response.headers['X-Server-Time'] = datetime.datetime.now().replace(microsecond=0).isoformat()

    return data