from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


SEVERITY_WEIGHTS = {
    "LOW": 5,
    "MEDIUM": 12,
    "HIGH": 25,
    "CRITICAL": 40,
}


@dataclass(frozen=True)
class PriorityResult:
    score: int
    band: str
    components: dict[str, int]
    strongest_signal: str | None


def financial_component(exposure: Decimal) -> int:
    if exposure >= Decimal("10000"):
        return 15
    if exposure >= Decimal("5000"):
        return 12
    if exposure >= Decimal("1000"):
        return 8
    if exposure >= Decimal("250"):
        return 4
    if exposure > 0:
        return 1
    return 0


def peer_component(robust_z_values: Iterable[float]) -> int:
    maximum = max((abs(value) for value in robust_z_values), default=0.0)
    if maximum >= 5:
        return 15
    if maximum >= 3:
        return 10
    return 0


def graph_component(
    *,
    shared_provider_count: int,
    max_shared_members_with_peer: int,
) -> int:
    if max_shared_members_with_peer >= 3:
        return 15
    if max_shared_members_with_peer >= 2:
        return 10
    if shared_provider_count >= 3:
        return 5
    return 0


def calculate_priority(
    *,
    rule_severities: Iterable[str],
    is_model_anomaly: bool,
    peer_robust_z_values: Iterable[float],
    shared_provider_count: int,
    max_shared_members_with_peer: int,
    financial_exposure: Decimal,
) -> PriorityResult:
    rule_score = min(
        sum(SEVERITY_WEIGHTS.get(severity, 0) for severity in rule_severities),
        50,
    )
    model_score = 20 if is_model_anomaly else 0
    peer_score = peer_component(peer_robust_z_values)
    network_score = graph_component(
        shared_provider_count=shared_provider_count,
        max_shared_members_with_peer=max_shared_members_with_peer,
    )
    money_score = financial_component(financial_exposure)

    components = {
        "rules": rule_score,
        "model_anomaly": model_score,
        "peer_deviation": peer_score,
        "network": network_score,
        "financial_exposure": money_score,
    }
    score = min(sum(components.values()), 100)

    if score >= 75:
        band = "CRITICAL"
    elif score >= 50:
        band = "HIGH"
    elif score >= 25:
        band = "MEDIUM"
    else:
        band = "LOW"

    strongest_signal = None
    if any(components.values()):
        strongest_signal = max(
            components,
            key=lambda key: components[key],
        )

    return PriorityResult(
        score=score,
        band=band,
        components=components,
        strongest_signal=strongest_signal,
    )
