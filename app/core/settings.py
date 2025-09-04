from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    config = Settings()
    return config

if __name__ == "__main__":
    settings = get_settings()
    print(f"Loaded APP_NAME setting: {settings.APP_NAME}")
    print(f"Loaded DATABASE_URI setting: {settings.DATABASE_URL}")

