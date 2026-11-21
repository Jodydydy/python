from fastapi import FastAPI

app = FastAPI()

my_awesome_api = FastAPI()

@my_awesome_api.get('/')
async def root():
    return {'message': 'Hello world'}

#@app.get('/')
#async def root():
#    return {'message': 'Hello world'}