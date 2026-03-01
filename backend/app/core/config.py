from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "FinFlow AI API"
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(default="sqlite:///./finflow.db")

    ai_provider: str = Field(default="claude")
    claude_api_key: str | None = None
    gemini_api_key: str | None = None
    grok_api_key: str | None = None

    @property
    def supported_ai_providers(self) -> tuple[str, ...]:
        return ("claude", "gemini", "grok")


@lru_cache
def get_settings() -> Settings:
    return Settings()
