import time

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    last_error: Exception | None = None

    for _ in range(30):
        try:
            with GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            ) as driver:
                driver.verify_connectivity()
            print("Neo4j is ready")
            return
        except ServiceUnavailable as exc:
            last_error = exc
            time.sleep(2)

    raise RuntimeError("Neo4j did not become ready") from last_error


if __name__ == "__main__":
    main()
