import re
from typing import Annotated

from fastapi import FastAPI, HTTPException, Header, Request

app = FastAPI()

pattern = r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"

@app.get('/headers')
async def get_headers(request: Request):


    user_agent = request.headers.get('User-Agent')
    accept_language = request.headers.get('Accept-Language')

    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="неверный запрос")

    if not re.fullmatch(pattern, accept_language):
        raise HTTPException(status_code=400, detail="неверный запрос")    

    return {'User-Agent': user_agent, 'Accept-Language': accept_language}