from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    auth_token: str
    scope: str
    token_url: str
    api_url: str
    database_url: str
    temperature: float
    max_tokens: int
    stream: bool
    model: str

    model_config = SettingsConfigDict(
        env_file =".env",
        env_file_encoding="utf-8",
    )


