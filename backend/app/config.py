from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    llm_provider: Literal["anthropic", "openai", "groq"] = "groq"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    database_url: str = "postgresql+asyncpg://advocatus:password@localhost:5432/advocatus"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
