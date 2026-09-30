from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    access_token_expire_minutes: int = 60
    transformer_model: str = "HuggingFaceTB/SmolLM2-360M-Instruct"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_must_be_configured(cls, value: str) -> str:
        if len(value.strip()) < 32 or value.startswith("replace-this"):
            raise ValueError("JWT_SECRET_KEY must be a random secret with at least 32 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
