from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    ADMIN: int
    GROUP_ID: int
    DB_NAME: str = 'database.db'
    LOG_TYPE: str = 'console'

    @field_validator('LOG_TYPE')
    def check_log_type(cls, v: str):
        v = v.lower()
        if v not in ['console', 'file']:
            raise ValueError("LOG_TYPE должен быть 'console' или 'file'")
        return v

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
