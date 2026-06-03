from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    SEC_USER_AGENT: str
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()