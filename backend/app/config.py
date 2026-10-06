from functools import lru_cache

from pydantic import Field, model_validator
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
    session_cookie_name: str = Field(default="cg_session")
    csrf_cookie_name: str = Field(default="cg_csrf")
    auth_token_ttl_minutes: int = Field(default=30, ge=5, le=1440)
    login_rate_limit_attempts: int = Field(default=5, ge=1, le=100)
    login_rate_limit_window_seconds: int = Field(default=900, ge=60, le=86400)
    frontend_base_url: str = Field(default="http://localhost:5173")

    email_delivery_mode: str = Field(default="smtp")
    mail_host: str = Field(default="localhost")
    mail_port: int = Field(default=1025, ge=1, le=65535)
    mail_user: str | None = Field(default=None)
    mail_password: str | None = Field(default=None)
    mail_from: str = Field(default="noreply@example.local")
    mail_use_tls: bool = Field(default=False)

    log_level: str = Field(default="INFO")
    otel_enabled: bool = Field(default=False)
    mlflow_tracking_uri: str = Field(default="sqlite:///mlflow.db")
    model_artifact_dir: str = Field(default="artifacts/models")

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env.lower() != "production":
            return self

        errors: list[str] = []

        if not self.frontend_origin.startswith("https://"):
            errors.append("FRONTEND_ORIGIN must use HTTPS in production")
        if not self.frontend_base_url.startswith("https://"):
            errors.append("FRONTEND_BASE_URL must use HTTPS in production")
        if len(self.session_secret) < 32 or self.session_secret == "development-only-change-me":
            errors.append("SESSION_SECRET must be at least 32 non-default characters")
        if "change-me" in self.database_url:
            errors.append("DATABASE_URL must not use development credentials")
        if self.neo4j_password == "change-me":
            errors.append("NEO4J_PASSWORD must not use the development placeholder")
        if "@" not in self.redis_url:
            errors.append("REDIS_URL must include authentication in production")
        if self.email_delivery_mode.lower() == "smtp":
            if self.mail_host in {"localhost", "mailpit"}:
                errors.append("MAIL_HOST must reference a production SMTP service")
            if not self.mail_use_tls:
                errors.append("MAIL_USE_TLS must be enabled for production SMTP")

        if errors:
            raise ValueError("; ".join(errors))

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
