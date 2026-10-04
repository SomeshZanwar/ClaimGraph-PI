from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import bindparam, select, text
from sqlalchemy.orm import Session

from app.casework.prioritization import calculate_priority
from app.db.models import (
    CaseEvidence,
    ClaimModelScore,
    GraphRun,
    InvestigationCase,
    ModelRun,
    ProviderGraphMetric,
    RiskSignal,
    RuleRun,
)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


def evidence_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        _json_safe(payload),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _latest_completed(session: Session, model: type[Any], order_column: Any) -> Any:
    return session.scalar(
        select(model)
        .where(model.status == "COMPLETED")
        .order_by(order_column.desc())
        .limit(1)
    )


def _signal_claim_ids(signal: RiskSignal) -> set[str]:
    if signal.entity_type == "CLAIM":
        return {signal.entity_id}

    if signal.entity_type in {"CLAIM_PAIR", "CLAIM_GROUP"}:
        return {value for value in signal.entity_id.split(":") if value}

    if signal.entity_type == "CLAIM_LINE":
        claim_id = signal.evidence.get("claim_record_id")
        return {str(claim_id)} if claim_id else set()

    return set()


def _fetch_claim_rows(
    session: Session,
    claim_ids: set[str],
) -> dict[str, dict[str, Any]]:
    if not claim_ids:
        return {}

    statement = text(
        """
        select
            f.claim_record_id,
            f.ingestion_batch_id,
            f.beneficiary_id,
            f.claim_id,
            f.claim_from_date,
            f.claim_through_date,
            f.line_count,
            f.provider_count,
            f.procedure_count,
            f.total_payment_amount,
            f.total_allowed_charge_amount,
            f.total_deductible_amount,
            f.total_coinsurance_amount,
            b.source_filename,
            b.source_sha256
        from analytics.fact_claims f
        inner join raw.ingestion_batches b
            on b.id::text = f.ingestion_batch_id
        where f.claim_record_id in :claim_ids
        """
    ).bindparams(bindparam("claim_ids", expanding=True))

    rows = session.execute(
        statement,
        {"claim_ids": sorted(claim_ids)},
    ).mappings()

    return {
        str(row["claim_record_id"]): dict(row)
        for row in rows
    }


def _fetch_claim_providers(
    session: Session,
    claim_ids: set[str],
) -> dict[str, list[str]]:
    if not claim_ids:
        return {}

    statement = text(
        """
        select distinct claim_record_id, provider_npi
        from analytics.fact_claim_lines
        where
            claim_record_id in :claim_ids
            and provider_npi is not null
        order by claim_record_id, provider_npi
        """
    ).bindparams(bindparam("claim_ids", expanding=True))

    mapping: dict[str, list[str]] = {}
    for row in session.execute(
        statement,
        {"claim_ids": sorted(claim_ids)},
    ).mappings():
        mapping.setdefault(str(row["claim_record_id"]), []).append(
            str(row["provider_npi"])
        )
    return mapping


def _fetch_peer_metrics(
    session: Session,
    provider_ids: set[str],
) -> dict[str, dict[str, Any]]:
    if not provider_ids:
        return {}

    statement = text(
        """
        select *
        from analytics.mart_provider_peer_metrics
        where provider_npi in :provider_ids
        """
    ).bindparams(bindparam("provider_ids", expanding=True))

    return {
        str(row["provider_npi"]): dict(row)
        for row in session.execute(
            statement,
            {"provider_ids": sorted(provider_ids)},
        ).mappings()
    }


def compose_cases(session: Session) -> list[InvestigationCase]:
    latest_rule_run = _latest_completed(
        session,
        RuleRun,
        RuleRun.started_at,
    )
    latest_model_run = _latest_completed(
        session,
        ModelRun,
        ModelRun.trained_at,
    )
    latest_graph_run = _latest_completed(
        session,
        GraphRun,
        GraphRun.started_at,
    )

    rule_signals: list[RiskSignal] = []
    if latest_rule_run is not None:
        rule_signals = list(
            session.scalars(
                select(RiskSignal).where(
                    RiskSignal.rule_run_id == latest_rule_run.id
                )
            )
        )

    model_scores: dict[str, ClaimModelScore] = {}
    if latest_model_run is not None:
        model_scores = {
            score.claim_record_id: score
            for score in session.scalars(
                select(ClaimModelScore).where(
                    ClaimModelScore.model_run_id == latest_model_run.id
                )
            )
        }

    graph_metrics: dict[str, ProviderGraphMetric] = {}
    if latest_graph_run is not None:
        graph_metrics = {
            metric.provider_npi: metric
            for metric in session.scalars(
                select(ProviderGraphMetric).where(
                    ProviderGraphMetric.graph_run_id == latest_graph_run.id
                )
            )
        }

    claim_rule_signals: dict[str, list[RiskSignal]] = {}
    candidate_claim_ids: set[str] = set()

    for signal in rule_signals:
        for claim_id in _signal_claim_ids(signal):
            candidate_claim_ids.add(claim_id)
            claim_rule_signals.setdefault(claim_id, []).append(signal)

    for claim_id, score in model_scores.items():
        if score.is_anomaly:
            candidate_claim_ids.add(claim_id)

    graph_candidate_providers = {
        provider_npi
        for provider_npi, metric in graph_metrics.items()
        if metric.max_shared_members_with_peer >= 2
        or metric.shared_provider_count >= 3
    }

    if graph_candidate_providers:
        statement = text(
            """
            select distinct claim_record_id
            from analytics.fact_claim_lines
            where provider_npi in :provider_ids
            """
        ).bindparams(bindparam("provider_ids", expanding=True))
        candidate_claim_ids.update(
            str(value)
            for value in session.execute(
                statement,
                {"provider_ids": sorted(graph_candidate_providers)},
            ).scalars()
        )

    peer_outlier_rows = session.execute(
        text(
            """
            select provider_npi
            from analytics.mart_provider_peer_metrics
            where
                peer_comparison_status = 'COMPARABLE'
                and abs(robust_z_avg_allowed) >= 3
            """
        )
    ).scalars()
    peer_candidate_providers = {str(value) for value in peer_outlier_rows}

    if peer_candidate_providers:
        statement = text(
            """
            select distinct claim_record_id
            from analytics.fact_claim_lines
            where provider_npi in :provider_ids
            """
        ).bindparams(bindparam("provider_ids", expanding=True))
        candidate_claim_ids.update(
            str(value)
            for value in session.execute(
                statement,
                {"provider_ids": sorted(peer_candidate_providers)},
            ).scalars()
        )

    claim_rows = _fetch_claim_rows(session, candidate_claim_ids)
    claim_providers = _fetch_claim_providers(session, candidate_claim_ids)
    all_provider_ids = {
        provider
        for providers in claim_providers.values()
        for provider in providers
    }
    peer_metrics = _fetch_peer_metrics(session, all_provider_ids)

    generated_cases: list[InvestigationCase] = []
    now = datetime.now(UTC)

    for claim_record_id in sorted(candidate_claim_ids):
        claim = claim_rows.get(claim_record_id)
        if claim is None:
            continue

        providers = claim_providers.get(claim_record_id, [])
        rules = claim_rule_signals.get(claim_record_id, [])
        model_score = model_scores.get(claim_record_id)
        peers = [
            peer_metrics[provider]
            for provider in providers
            if provider in peer_metrics
        ]
        graph = [
            graph_metrics[provider]
            for provider in providers
            if provider in graph_metrics
        ]

        peer_z_values = [
            float(peer["robust_z_avg_allowed"])
            for peer in peers
            if peer.get("robust_z_avg_allowed") is not None
        ]
        max_shared_provider_count = max(
            (metric.shared_provider_count for metric in graph),
            default=0,
        )
        max_shared_members = max(
            (metric.max_shared_members_with_peer for metric in graph),
            default=0,
        )
        exposure = Decimal(str(claim["total_allowed_charge_amount"] or 0))

        priority = calculate_priority(
            rule_severities=[signal.severity for signal in rules],
            is_model_anomaly=bool(model_score and model_score.is_anomaly),
            peer_robust_z_values=peer_z_values,
            shared_provider_count=max_shared_provider_count,
            max_shared_members_with_peer=max_shared_members,
            financial_exposure=exposure,
        )

        payload = {
            "claim": _json_safe(claim),
            "providers": providers,
            "rule_signals": [
                {
                    "rule_id": signal.rule_id,
                    "rule_version": signal.rule_version,
                    "severity": signal.severity,
                    "explanation": signal.explanation,
                    "evidence": signal.evidence,
                    "rule_run_id": str(signal.rule_run_id),
                }
                for signal in rules
            ],
            "model_signal": (
                {
                    "model_run_id": str(model_score.model_run_id),
                    "model_version": latest_model_run.model_version
                    if latest_model_run
                    else None,
                    "model_type": latest_model_run.model_type
                    if latest_model_run
                    else None,
                    "anomaly_score": str(model_score.anomaly_score),
                    "is_anomaly": model_score.is_anomaly,
                    "feature_deviation_context": model_score.feature_deviation_context,
                    "note": "The anomaly score is not a fraud probability.",
                }
                if model_score is not None
                else None
            ),
            "peer_signals": [_json_safe(peer) for peer in peers],
            "graph_signals": [
                {
                    "provider_npi": metric.provider_npi,
                    "member_count": metric.member_count,
                    "shared_provider_count": metric.shared_provider_count,
                    "max_shared_members_with_peer": metric.max_shared_members_with_peer,
                    "component_provider_count": metric.component_provider_count,
                    "component_member_count": metric.component_member_count,
                    "graph_run_id": str(metric.graph_run_id),
                }
                for metric in graph
            ],
            "financial_exposure": str(exposure),
            "priority": {
                "score": priority.score,
                "band": priority.band,
                "components": priority.components,
                "strongest_signal": priority.strongest_signal,
                "note": "Workflow priority only; not a fraud probability or claim decision.",
            },
            "lineage": {
                "ingestion_batch_id": claim["ingestion_batch_id"],
                "source_filename": claim["source_filename"],
                "source_sha256": claim["source_sha256"],
            },
            "limitations": [
                "Source data is synthetic CMS DE-SynPUF data.",
                "Synthetic provider identifiers do not identify real providers.",
                "Signals require human investigation and are not proof of fraud.",
            ],
        }
        safe_payload = _json_safe(payload)
        digest = evidence_hash(safe_payload)

        case_key = f"CLAIM:{claim_record_id}"
        case = session.scalar(
            select(InvestigationCase).where(
                InvestigationCase.case_key == case_key
            )
        )

        if case is None:
            case = InvestigationCase(
                case_key=case_key,
                claim_record_id=claim_record_id,
                status="NEW",
                priority_score=Decimal(priority.score),
                priority_band=priority.band,
                financial_exposure=exposure,
                strongest_signal=priority.strongest_signal,
                current_evidence_hash=digest,
                created_at=now,
                updated_at=now,
            )
            session.add(case)
            session.flush()
        else:
            case.priority_score = Decimal(priority.score)
            case.priority_band = priority.band
            case.financial_exposure = exposure
            case.strongest_signal = priority.strongest_signal
            case.current_evidence_hash = digest
            case.updated_at = now

        existing_evidence = session.scalar(
            select(CaseEvidence).where(
                CaseEvidence.case_id == case.id,
                CaseEvidence.evidence_hash == digest,
            )
        )
        if existing_evidence is None:
            session.add(
                CaseEvidence(
                    case_id=case.id,
                    evidence_hash=digest,
                    payload=safe_payload,
                    generated_at=now,
                )
            )

        generated_cases.append(case)

    session.commit()
    return generated_cases
