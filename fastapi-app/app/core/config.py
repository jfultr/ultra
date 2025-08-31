from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "FastAPI App"
    API_V1_STR: str = "/api"

    # Security
    SECRET_KEY: str = "supersecretkey-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings: Settings = get_settings()


