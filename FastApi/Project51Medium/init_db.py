import asyncpg
import asyncio

DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydatabase"

async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS Todo (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            completed boolean
        )

    ''')
    await conn.close()

asyncio.run(create_table())