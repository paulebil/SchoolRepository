from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, SecretStr
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    FRONTEND_HOST: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_FROM: EmailStr
    SMTP_FROM_NAME: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: SecretStr
    SMTP_SERVER: str
    SMTP_STARTTLS: bool
    SMTP_SSL_TLS: bool
    SMTP_DEBUG: bool
    USE_CREDENTIALS: bool

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore"
    )

    # Un-comment this lines of code to print the loaded settings
    # def __init__(self, **values):
    #     super().__init__(**values)
    #     print("\nLoaded settings:")
    #     for key, value in self.model_dump().items():
    #         print(f"{key}: {value} ({type(value).__name__})")

@lru_cache()
def get_settings() -> Settings:
    config = Settings()
    return config

if __name__ == "__main__":
    settings = get_settings()
    # print(f"Loaded APP_NAME setting: {settings.APP_NAME}")
    # print(f"Loaded DATABASE_URI setting: {settings.DATABASE_URL}")
    #
