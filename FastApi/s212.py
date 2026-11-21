from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel


class Item(BaseModel):
    num1: int=0
    num2: int=0


app = FastAPI()


@app.post("/calculate")
async def update_item(item: Item):
    item_dict = {'result': item.num1 + item.num2}
    return item_dict