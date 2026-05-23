from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-mini"
    default_llm_provider: str = "mock"
    default_vision_provider: str = "mock"
    storage_dir: str = "./storage"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_api_base_url: str = "http://127.0.0.1:8000"
    enable_vision: bool = True
    enable_critic: bool = True
    enable_repair: bool = True
    max_repair_loops: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_dir).resolve()

    @property
    def profiles_path(self) -> Path:
        return self.storage_path / "profiles"

    @property
    def uploads_path(self) -> Path:
        return self.storage_path / "uploads"

    @property
    def decks_path(self) -> Path:
        return self.storage_path / "decks"

    @property
    def config_path(self) -> Path:
        return self.storage_path / "config"

    @property
    def logs_path(self) -> Path:
        return Path("logs").resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
