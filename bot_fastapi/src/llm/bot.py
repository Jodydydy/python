from dataclasses import dataclass
import uuid

import httpx

from core.config import Settings
from interfaces.baseLLMClient import BaseLLMClient

@dataclass(slots=True)
class GigaChatClient(BaseLLMClient):

    settings: Settings 
    async_client: httpx.AsyncClient

    async def get_token(self) -> str:
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
    


    async def generate_response(self, messages: list[dict[str, str]]) -> str:
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






    