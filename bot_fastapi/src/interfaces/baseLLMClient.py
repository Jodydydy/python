class BaseLLMClient:

    async def  generate_response(self, messages: list) -> str:
        raise NotImplementedError