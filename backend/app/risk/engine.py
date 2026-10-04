from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from importlib.resources import files
from typing import Any

import yaml
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import RiskSignal, RuleRun


class RuleDefinition(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    version: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1)
    entity_type: str = Field(min_length=1, max_length=32)
    severity: str = Field(pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    explanation: str = Field(min_length=1)
    sql: str = Field(min_length=1)


class RuleFile(BaseModel):
    rules: list[RuleDefinition]


def load_rule_definitions() -> list[RuleDefinition]:
    source = files("app.risk.rules").joinpath("definitions.yml").read_text(encoding="utf-8")
    payload = yaml.safe_load(source)
    parsed = RuleFile.model_validate(payload)

    rule_keys = [(rule.id, rule.version) for rule in parsed.rules]
    if len(rule_keys) != len(set(rule_keys)):
        raise ValueError("Duplicate rule ID/version pairs are not allowed")

    return parsed.rules


def ruleset_hash(rules: list[RuleDefinition]) -> str:
    canonical = [
        {
            "id": rule.id,
            "version": rule.version,
            "entity_type": rule.entity_type,
            "severity": rule.severity,
            "sql": rule.sql,
        }
        for rule in rules
    ]
    serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def run_rules(
    session: Session,
    rules: list[RuleDefinition] | None = None,
) -> RuleRun:
    active_rules = rules or load_rule_definitions()
    run = RuleRun(
        ruleset_hash=ruleset_hash(active_rules),
        status="STARTED",
        started_at=datetime.now(UTC),
        signal_count=0,
    )
    session.add(run)
    session.commit()

    try:
        for rule in active_rules:
            rows = session.execute(text(rule.sql)).mappings()

            for row in rows:
                mapping = dict(row)
                entity_id = mapping.pop("entity_id", None)
                observed_value = mapping.pop("observed_value", None)
                threshold_value = mapping.pop("threshold_value", None)

                if entity_id is None:
                    raise ValueError(f"Rule {rule.id} returned no entity_id")

                signal = RiskSignal(
                    rule_run_id=run.id,
                    rule_id=rule.id,
                    rule_version=rule.version,
                    entity_type=rule.entity_type,
                    entity_id=str(entity_id),
                    severity=rule.severity,
                    explanation=rule.explanation,
                    evidence=_json_safe(mapping),
                    observed_value=_decimal_or_none(observed_value),
                    threshold_value=_decimal_or_none(threshold_value),
                    evaluated_at=datetime.now(UTC),
                )
                session.add(signal)
                run.signal_count += 1

        run.status = "COMPLETED"
        run.completed_at = datetime.now(UTC)
        session.commit()
        session.refresh(run)
        return run
    except Exception as exc:
        session.rollback()
        failed_run = session.get(RuleRun, run.id)
        if failed_run is not None:
            failed_run.status = "FAILED"
            failed_run.completed_at = datetime.now(UTC)
            failed_run.error_message = str(exc)[:2000]
            session.commit()
        raise
