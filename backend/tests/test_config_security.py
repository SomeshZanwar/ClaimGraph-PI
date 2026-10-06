import pytest
from pydantic import ValidationError

from app.config import Settings


def production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": "production",
        "frontend_origin": "https://claimgraph.example.test",
        "frontend_base_url": "https://claimgraph.example.test",
        "database_url": "postgresql+psycopg://claimgraph:strong-db-password@postgres:5432/claimgraph",
        "neo4j_password": "strong-neo4j-password",
        "redis_url": "redis://:strong-redis-password@redis:6379/0",
        "session_secret": "a-very-long-production-session-secret-value",
        "email_delivery_mode": "smtp",
        "mail_host": "smtp.example.test",
        "mail_use_tls": True,
    }
    values.update(overrides)
    return Settings(**values)


def test_production_settings_accept_secure_configuration() -> None:
    settings = production_settings()

    assert settings.app_env == "production"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frontend_origin", "http://claimgraph.example.test"),
        ("frontend_base_url", "http://claimgraph.example.test"),
        ("session_secret", "short-development"),
        ("database_url", "postgresql+psycopg://claimgraph:change-me@postgres:5432/claimgraph"),
        ("neo4j_password", "change-me"),
        ("redis_url", "redis://redis:6379/0"),
        ("mail_host", "mailpit"),
        ("mail_use_tls", False),
    ],
)
def test_production_settings_reject_unsafe_configuration(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError):
        production_settings(**{field: value})
