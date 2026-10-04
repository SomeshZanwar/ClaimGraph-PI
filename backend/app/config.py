from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="development")
    app_name: str = Field(default="ClaimGraph PI")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000, ge=1, le=65535)
    frontend_origin: str = Field(default="http://localhost:5173")

    database_url: str = Field(
        default="postgresql+psycopg://claimgraph:change-me@localhost:5432/claimgraph"
    )
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="change-me")
    redis_url: str = Field(default="redis://localhost:6379/0")

    session_secret: str = Field(default="development-only-change-me", min_length=16)
    session_ttl_minutes: int = Field(default=60, ge=5, le=1440)

    log_level: str = Field(default="INFO")
    otel_enabled: bool = Field(default=False)
    mlflow_tracking_uri: str = Field(default="file:./mlruns")
    model_artifact_dir: str = Field(default="artifacts/models")


@lru_cache
def get_settings() -> Settings:
    return Settings()
