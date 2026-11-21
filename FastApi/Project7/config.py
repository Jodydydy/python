from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    mode: str
    docs_user: str
    docs_password: str

    model_config = SettingsConfigDict(env_file='Project7/.env')    


@lru_cache
def get_setting():
    return Settings()    