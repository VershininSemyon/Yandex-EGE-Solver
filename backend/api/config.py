
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        extra='ignore'
    )

    UVICORN_RELOAD: bool = False
    UVICORN_WORKERS_COUNT: int = 4
    CORS_ORIGINS: list[str] = ["http://localhost", "http://127.0.0.1"]


settings = Settings()
