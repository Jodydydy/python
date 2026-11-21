from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = "mongodb://localhost:27017"
DB_NAME = "mydatabase"

async def get_db():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()         