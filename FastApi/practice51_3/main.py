from fastapi import FastAPI, Depends
from pydantic import BaseModel
from database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

app = FastAPI()

class Item(BaseModel):

    name: str

@app.post('/items')
async def create_item(item: Item, db: AsyncIOMotorDatabase = Depends(get_db)):

    result = await db.items.insert_one(item.dict())
    return {'message': 'Item added successfully!', 'id': str(result.inserted_id)}