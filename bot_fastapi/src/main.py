from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from models.user import CONTEXT_LIMITS
from core.config import Settings
from core.database import MessageRepository, SQLAlchemyMessageRepository
from llm.bot import BaseLLMClient, GigaChatClient
from service.generate_answer import llm_generate_answer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from loguru import logger
import httpx

from models.messsage import MessageRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    async with httpx.AsyncClient(timeout=90.0, verify=False) as client:
        settings = Settings()
        app.state.http_client = client
        app.state.settings = settings
        engine = create_async_engine(settings.database_url)
        app.state.engine = engine
        app.state.SessionLocal = async_sessionmaker(bind=app.state.engine, expire_on_commit=False)

        try:
            yield
        finally:
            await engine.dispose()       


app = FastAPI(lifespan=lifespan)




def get_llm_client(request: Request) -> BaseLLMClient:
    return GigaChatClient(settings=request.app.state.settings, async_client=request.app.state.http_client)


def get_msg_repository(request: Request) -> MessageRepository:
    return SQLAlchemyMessageRepository(SessionLocal=request.app.state.SessionLocal)


@app.post('/chat', response_model=dict[str, str])
async def chat(user_id: int, username: str, text: str, llm_client: BaseLLMClient = Depends(get_llm_client), repository: MessageRepository = Depends(get_msg_repository)) -> dict[str, str]:
    logger.info(f"User: {user_id} sent message")
    
    message = MessageRequest(user_id=user_id, username=username, text=text)
    answer = await llm_generate_answer(message=message, llm_client=llm_client, repository=repository)

    logger.info(f"Answer for User: {user_id} successfully generated")
    return {'Answer': answer}


@app.patch('/set_context', response_model=dict[str, str])
async def set_context(user_id: int, mode: str, repository: MessageRepository = Depends(get_msg_repository)) -> dict[str, str]:

    if mode not in CONTEXT_LIMITS:
        logger.warning(f"Mode: {mode} is incorrect. Such context mode doesnt exist")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Context mode doesnt exist. Try short|normal|long")
    
    await repository.set_context_mode(user_id=user_id, context_mode=mode)

    logger.info(f"User: {user_id} set context mode: {mode} successfully!")
    return {'message': f'Now context is {mode}'}
    
