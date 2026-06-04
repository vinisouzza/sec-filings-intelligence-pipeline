from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    SEC_USER_AGENT: str
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()