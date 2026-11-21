class MessageRepository:

    async def get_user_messages(self, user_id: int, username: str, text: str) -> list:
        raise NotImplementedError

    async def add_new_message(self, user_id: int, content):
        raise NotImplementedError

    async def set_context_mode(self, user_id, context_mode):
        raise NotImplementedError