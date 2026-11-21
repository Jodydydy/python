from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from interfaces.messageRepository import MessageRepository
from models.user import User, context_mode
from models.messsage import Message
from sqlalchemy.ext.asyncio import AsyncSession

    

class SQLAlchemyMessageRepository(MessageRepository):

    def __init__(self, SessionLocal):
        self.SessionLocal = SessionLocal

    async def get_user_messages(self, user_id: int, username: str, text: str) -> list:
        
        async with self.SessionLocal() as session:
        
            insert_stmt = insert(User).values({'id':user_id, 'username':username, 'context_mode':"normal"})
            user_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
            await session.execute(user_stmt)
        
            user = await get_user_by_id(session=session, user_id=user_id)
                    
            session.add(Message(user_id=user_id, role='user', content=text) )         
        
            await session.commit()  
            limit = context_mode.get(user.context_mode, context_mode["normal"])
            history = await get_recent_messages(session=session, user_id=user_id, limit=limit)              
        
        messages = [{'role': msg.role, 'content': msg.content} for msg in reversed(history)]

        return messages


    async def add_new_message(self, user_id: int, content):
        async with self.SessionLocal() as session:
            session.add(Message(user_id=user_id, role='assistant', content=content))
            await session.commit() 


    async def set_context_mode(self, user_id, context_mode):
        async with self.SessionLocal() as session:
            insert_stmt = insert(User).values({'id':user_id, 'context_mode':context_mode})
            user_stmt = insert_stmt.on_conflict_do_update(index_elements=['id'], set_={'context_mode':context_mode})
            await session.execute(user_stmt)

            await session.commit()


async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))

    return result.scalar_one_or_none() 


async def get_recent_messages(session: AsyncSession, user_id: int, limit: int):

    result = await session.execute(select(Message).where(Message.user_id == user_id).order_by(Message.id.desc()).limit(limit))

    return result.scalars().all()





