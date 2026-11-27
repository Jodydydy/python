
class BaseLLMClient:
    __slots__ = ()
    async def  generate_response(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError