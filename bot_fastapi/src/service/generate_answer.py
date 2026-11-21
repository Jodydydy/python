from interfaces.messageRepository import MessageRepository
from interfaces.baseLLMClient import BaseLLMClient
from models.messsage import MessageRequest


async def llm_generate_answer(message: MessageRequest, llm_client: BaseLLMClient, repository: MessageRepository) -> str:
   
    messages = await repository.get_user_messages(message.user_id, message.username, message.text)

    answer = await llm_client.generate_response(messages)
    await repository.add_new_message(user_id=message.user_id, content=answer)

    return answer