from __future__ import annotations

from dataclasses import dataclass

from neo4j import GraphDatabase
from redis import Redis
from sqlalchemy import text

from app.config import get_settings
from app.db.session import engine


@dataclass(frozen=True)
class DependencyStatus:
    database: bool
    neo4j: bool
    redis: bool

    @property
    def ready(self) -> bool:
        return self.database and self.neo4j and self.redis

    def as_dict(self) -> dict[str, str]:
        return {
            "database": "ok" if self.database else "unavailable",
            "neo4j": "ok" if self.neo4j else "unavailable",
            "redis": "ok" if self.redis else "unavailable",
        }


def _check_database() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_neo4j() -> bool:
    settings = get_settings()
    try:
        with GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            connection_timeout=2.0,
        ) as driver:
            driver.verify_connectivity()
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    settings = get_settings()
    try:
        client = Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        return bool(client.ping())
    except Exception:
        return False


def check_dependencies() -> DependencyStatus:
    return DependencyStatus(
        database=_check_database(),
        neo4j=_check_neo4j(),
        redis=_check_redis(),
    )
