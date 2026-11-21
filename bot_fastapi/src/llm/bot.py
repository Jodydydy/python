import uuid

from interfaces.baseLLMClient import BaseLLMClient


class GigaChatClient(BaseLLMClient):

    def __init__(self, settings, async_client):
        self.settings = settings
        self.async_client = async_client

    async def get_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {self.settings.auth_token}'
        }
        data = {'scope':self.settings.scope}
        response = await self.async_client.post(self.settings.token_url, headers=headers, data=data)

        response.raise_for_status()

        return response.json()['access_token']
    


    async def generate_response(self, messages: list) -> str:
        token = await self.get_token()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        payload ={
            "model": self.settings.model,
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
            "stream": self.settings.stream
        }

        response = await self.async_client.post(self.settings.api_url, headers=headers, json=payload)

        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']






    