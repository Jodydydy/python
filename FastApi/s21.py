from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get('/', response_class=FileResponse)
async def root():
    return 'index.html'
