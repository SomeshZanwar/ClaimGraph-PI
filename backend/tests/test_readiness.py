from app.readiness import DependencyStatus


def test_dependency_status_ready_when_all_dependencies_are_available() -> None:
    status = DependencyStatus(database=True, neo4j=True, redis=True)

    assert status.ready is True
    assert status.as_dict() == {
        "database": "ok",
        "neo4j": "ok",
        "redis": "ok",
    }


def test_dependency_status_reports_unavailable_dependency() -> None:
    status = DependencyStatus(database=True, neo4j=False, redis=True)

    assert status.ready is False
    assert status.as_dict()["neo4j"] == "unavailable"
