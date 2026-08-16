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

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        # asyncpg doesn't support channel_binding or sslmode (it expects ssl=require)
        url = url.replace("?channel_binding=require&", "?")
        url = url.replace("&channel_binding=require", "")
        url = url.replace("?channel_binding=require", "")
        url = url.replace("sslmode=require", "ssl=require")
        
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
