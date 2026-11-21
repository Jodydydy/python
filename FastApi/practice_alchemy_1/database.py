from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost/shop_db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False)

async def get_session():
    async with SessionLocal() as session: 
        yield session