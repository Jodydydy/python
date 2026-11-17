import requests
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from telebot.async_telebot import AsyncTeleBot
from models.user import User, context_mode, CONTEXT_LIMITS
from models.messsage import Message
from core.config import BOT_TOKEN, GIGACHAT_API_URL, GIGACHAT_MODEL, MAX_TOKENS, STREAM, TEMPERATURE, get_token 
from sqlalchemy.ext.asyncio import AsyncSession
from core.session import SessionLocal
import asyncio

bot = AsyncTeleBot(BOT_TOKEN)


async def generate_response(messages: list) -> str:
    token = get_token()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload ={
        "model": GIGACHAT_MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": STREAM
    }

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)

    return response.json()['choices'][0]['message']['content']


async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))

    return result.scalar_one_or_none() 


async def get_recent_messages(session: AsyncSession, user_id, limit: int):

    result = await session.execute(select(Message).where(Message.user_id == user_id).order_by(Message.id.desc()).limit(limit))

    return result.scalars().all()


@bot.message_handler(commands=['context'])
async def set_context_mode(message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2 or parts[-1] not in CONTEXT_LIMITS:
        await bot.send_message(message.chat.id, text="/context short|normal|long", parse_mode="HTML")
        return

    mode = parts[-1]

    async with SessionLocal() as session:
        insert_stmt = insert(User).values({'id':user_id, 'username':message.from_user.username, 'context_mode':mode})
        user_stmt = insert_stmt.on_conflict_do_update(index_elements=['id'], set_={'context_mode':mode})
        await session.execute(user_stmt)

        await session.commit()


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, "Привет, я твой первый бот!")


@bot.message_handler(content_types=['text'])
async def generate(message):

    user_id = message.from_user.id

    async with SessionLocal() as session:

        insert_stmt = insert(User).values({'id':user_id, 'username':message.from_user.username, 'context_mode':"normal"})
        user_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        await session.execute(user_stmt)

        user = await get_user_by_id(session=session, user_id=user_id)
            
        session.add(Message(user_id=user_id, role='user', content=message.text) )         

        await session.commit()  
        limit = context_mode.get(user.context_mode, context_mode["normal"])
        history = await get_recent_messages(session=session, user_id=user_id, limit=limit)              


    messages = [{'role': msg.role, 'content': msg.content} for msg in reversed(history)]


    answer = await generate_response(messages)
    async with SessionLocal() as session:
        session.add(Message(user_id=user_id, role='assistant', content=answer))
        await session.commit() 

    await bot.send_message(message.chat.id, text=answer, parse_mode="HTML")


def main():
    asyncio.run(bot.polling(non_stop=True, request_timeout=90))


if __name__ == "__main__":
    main()
    