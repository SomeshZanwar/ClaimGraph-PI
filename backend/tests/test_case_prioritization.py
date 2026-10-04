from decimal import Decimal

from app.casework.composer import evidence_hash
from app.casework.prioritization import calculate_priority


def test_priority_score_is_transparent_component_sum() -> None:
    result = calculate_priority(
        rule_severities=["HIGH", "MEDIUM"],
        is_model_anomaly=True,
        peer_robust_z_values=[3.5],
        shared_provider_count=1,
        max_shared_members_with_peer=0,
        financial_exposure=Decimal("1200"),
    )

    assert result.components == {
        "rules": 37,
        "model_anomaly": 20,
        "peer_deviation": 10,
        "network": 0,
        "financial_exposure": 8,
    }
    assert result.score == 75
    assert result.band == "CRITICAL"


def test_priority_score_is_not_probability_scaled() -> None:
    result = calculate_priority(
        rule_severities=[],
        is_model_anomaly=False,
        peer_robust_z_values=[],
        shared_provider_count=0,
        max_shared_members_with_peer=0,
        financial_exposure=Decimal("0"),
    )

    assert result.score == 0
    assert result.band == "LOW"


def test_evidence_hash_is_order_independent_for_mapping_keys() -> None:
    first = {"b": 2, "a": {"z": 1, "y": 2}}
    second = {"a": {"y": 2, "z": 1}, "b": 2}

    assert evidence_hash(first) == evidence_hash(second)
