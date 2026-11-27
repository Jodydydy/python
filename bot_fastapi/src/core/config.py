from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = Field(description="Bot`s token")
    auth_token: str = Field(description="Key for authorization token")
    scope: str = Field(description="Scope")
    token_url: str = Field(description="Token url")
    api_url: str = Field(description="API url")
    database_url: str = Field(description="Database url")
    temperature: float = Field(description="Creativity of the bot")
    max_tokens: int = Field(description="Maximum tokens per answer")
    stream: bool = Field(description="Stream answer activation")
    model: str = Field(description="Model name")

    model_config = SettingsConfigDict(
        env_file =".env",
        env_file_encoding="utf-8",
    )


