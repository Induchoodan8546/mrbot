from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "MRBot"
    app_version: str = "0.1.0"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    database_url: str = "sqlite:///./mrbot.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()