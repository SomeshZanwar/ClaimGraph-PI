from app.graph.analytics import compute_provider_metrics


def test_compute_provider_metrics_finds_shared_member_networks() -> None:
    metrics = compute_provider_metrics(
        [
            ("P1", "M1"),
            ("P1", "M2"),
            ("P2", "M2"),
            ("P2", "M3"),
            ("P3", "M9"),
        ]
    )
    by_provider = {metric.provider_npi: metric for metric in metrics}

    assert by_provider["P1"].member_count == 2
    assert by_provider["P1"].shared_provider_count == 1
    assert by_provider["P1"].max_shared_members_with_peer == 1
    assert by_provider["P1"].component_provider_count == 2
    assert by_provider["P1"].component_member_count == 3

    assert by_provider["P3"].shared_provider_count == 0
    assert by_provider["P3"].component_provider_count == 1
    assert by_provider["P3"].component_member_count == 1


def test_compute_provider_metrics_handles_empty_graph() -> None:
    assert compute_provider_metrics([]) == []
