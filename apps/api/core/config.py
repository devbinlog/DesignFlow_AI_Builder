from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 데이터베이스
    database_url: str = "postgresql+asyncpg://designflow:password@localhost:5432/designflow"

    # Anthropic
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"
    ai_max_tokens: int = 4096

    # 서버
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    max_file_size_mb: int = 10


settings = Settings()
