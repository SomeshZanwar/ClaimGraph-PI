from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import joblib
import mlflow
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import ClaimModelScore, ModelRun

FEATURE_NAMES = (
    "line_count",
    "provider_count",
    "procedure_count",
    "total_payment_amount",
    "total_allowed_charge_amount",
    "total_deductible_amount",
    "total_coinsurance_amount",
    "payment_to_allowed_ratio",
    "allowed_charge_per_line",
    "payment_per_line",
    "service_span_days",
)

FEATURE_SQL = """
select
    claim_record_id,
    line_count,
    provider_count,
    procedure_count,
    total_payment_amount,
    total_allowed_charge_amount,
    total_deductible_amount,
    total_coinsurance_amount,
    payment_to_allowed_ratio,
    allowed_charge_per_line,
    payment_per_line,
    service_span_days
from analytics.mart_claim_ml_features
order by claim_record_id
"""


@dataclass(frozen=True)
class FeatureSet:
    claim_ids: list[str]
    matrix: np.ndarray


@dataclass(frozen=True)
class FittedAnomalyModel:
    pipeline: Pipeline
    scores: np.ndarray
    threshold: float
    medians: np.ndarray
    mads: np.ndarray


def source_snapshot_hash(session: Session) -> str:
    hashes = list(
        session.execute(
            text(
                """
                select source_sha256
                from raw.ingestion_batches
                where status = 'COMPLETED'
                order by source_sha256
                """
            )
        ).scalars()
    )
    if not hashes:
        raise RuntimeError("No completed ingestion batches available for model training")

    digest = hashlib.sha256()
    for value in hashes:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def load_feature_set(session: Session) -> FeatureSet:
    rows = session.execute(text(FEATURE_SQL)).mappings().all()
    claim_ids = [str(row["claim_record_id"]) for row in rows]
    matrix = np.asarray(
        [
            [
                float(row[name]) if row[name] is not None else np.nan
                for name in FEATURE_NAMES
            ]
            for row in rows
        ],
        dtype=float,
    )
    return FeatureSet(claim_ids=claim_ids, matrix=matrix)


def fit_anomaly_model(
    matrix: np.ndarray,
    *,
    contamination: float = 0.05,
    random_state: int = 42,
) -> FittedAnomalyModel:
    if matrix.ndim != 2:
        raise ValueError("Feature matrix must be two-dimensional")
    if matrix.shape[0] < 2:
        raise ValueError("At least two rows are required to fit the anomaly model")
    if not 0 < contamination < 0.5:
        raise ValueError("contamination must be between 0 and 0.5")

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                IsolationForest(
                    n_estimators=250,
                    contamination=contamination,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    pipeline.fit(matrix)

    imputed = pipeline.named_steps["imputer"].transform(matrix)
    model = pipeline.named_steps["model"]
    scores = -model.decision_function(imputed)
    threshold = float(np.quantile(scores, 1 - contamination))

    medians = np.median(imputed, axis=0)
    mads = np.median(np.abs(imputed - medians), axis=0)

    return FittedAnomalyModel(
        pipeline=pipeline,
        scores=scores,
        threshold=threshold,
        medians=medians,
        mads=mads,
    )


def feature_deviation_context(
    row: np.ndarray,
    medians: np.ndarray,
    mads: np.ndarray,
    *,
    limit: int = 3,
) -> dict[str, Any]:
    deviations: list[tuple[float, dict[str, Any]]] = []

    for index, feature_name in enumerate(FEATURE_NAMES):
        mad = float(mads[index])
        if mad <= 0:
            continue

        value = float(row[index])
        median = float(medians[index])
        robust_z = (value - median) / (1.4826 * mad)
        deviations.append(
            (
                abs(robust_z),
                {
                    "feature": feature_name,
                    "value": value,
                    "training_median": median,
                    "robust_z": robust_z,
                },
            )
        )

    deviations.sort(key=lambda item: item[0], reverse=True)
    return {
        "type": "feature_deviation_context",
        "note": "Descriptive context only; these values are not causal explanations.",
        "top_deviations": [item[1] for item in deviations[:limit]],
    }


def _tracking_uri(uri: str) -> str:
    if uri.startswith("file:./"):
        return (Path.cwd() / uri.removeprefix("file:./")).resolve().as_uri()
    return uri


def train_and_score_claims(
    session: Session,
    *,
    contamination: float = 0.05,
    min_training_rows: int = 50,
) -> ModelRun:
    settings = get_settings()
    feature_set = load_feature_set(session)

    if len(feature_set.claim_ids) < min_training_rows:
        raise ValueError(
            f"Need at least {min_training_rows} claim rows for training; "
            f"found {len(feature_set.claim_ids)}"
        )

    snapshot_hash = source_snapshot_hash(session)
    now = datetime.now(UTC)
    model_version = f"claim-iforest-{now.strftime('%Y%m%dT%H%M%SZ')}-{snapshot_hash[:8]}"

    run = ModelRun(
        model_version=model_version,
        model_type="IsolationForest",
        source_snapshot_hash=snapshot_hash,
        status="STARTED",
        trained_at=now,
        training_row_count=len(feature_set.claim_ids),
        contamination=Decimal(str(contamination)),
        feature_names=list(FEATURE_NAMES),
        metrics={},
    )
    session.add(run)
    session.commit()

    try:
        fitted = fit_anomaly_model(
            feature_set.matrix,
            contamination=contamination,
        )

        imputed = fitted.pipeline.named_steps["imputer"].transform(feature_set.matrix)
        anomaly_flags = fitted.scores >= fitted.threshold
        anomaly_fraction = float(np.mean(anomaly_flags))

        metrics = {
            "training_rows": len(feature_set.claim_ids),
            "anomaly_fraction": anomaly_fraction,
            "score_p50": float(np.quantile(fitted.scores, 0.50)),
            "score_p95": float(np.quantile(fitted.scores, 0.95)),
            "score_max": float(np.max(fitted.scores)),
        }

        artifact_dir = Path(settings.model_artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_dir / f"{model_version}.joblib"
        artifact = {
            "model_version": model_version,
            "source_snapshot_hash": snapshot_hash,
            "feature_names": FEATURE_NAMES,
            "pipeline": fitted.pipeline,
            "anomaly_threshold": fitted.threshold,
            "training_medians": fitted.medians,
            "training_mads": fitted.mads,
        }
        joblib.dump(artifact, artifact_path)

        mlflow.set_tracking_uri(_tracking_uri(settings.mlflow_tracking_uri))
        mlflow.set_experiment("claimgraph-claim-anomaly")
        with mlflow.start_run(run_name=model_version):
            mlflow.log_params(
                {
                    "model_type": "IsolationForest",
                    "contamination": contamination,
                    "feature_count": len(FEATURE_NAMES),
                    "source_snapshot_hash": snapshot_hash,
                }
            )
            mlflow.log_metrics(
                {
                    key: float(value)
                    for key, value in metrics.items()
                    if isinstance(value, (int, float))
                }
            )
            mlflow.log_artifact(str(artifact_path))

        scored_at = datetime.now(UTC)
        for index, claim_id in enumerate(feature_set.claim_ids):
            context = feature_deviation_context(
                imputed[index],
                fitted.medians,
                fitted.mads,
            )
            session.add(
                ClaimModelScore(
                    model_run_id=run.id,
                    claim_record_id=claim_id,
                    anomaly_score=Decimal(str(float(fitted.scores[index]))),
                    is_anomaly=bool(anomaly_flags[index]),
                    feature_deviation_context=context,
                    scored_at=scored_at,
                )
            )

        run.status = "COMPLETED"
        run.completed_at = datetime.now(UTC)
        run.anomaly_threshold = Decimal(str(fitted.threshold))
        run.metrics = json.loads(json.dumps(metrics))
        run.artifact_path = str(artifact_path)
        session.commit()
        session.refresh(run)
        return run
    except Exception as exc:
        session.rollback()
        failed_run = session.scalar(
            select(ModelRun).where(ModelRun.id == run.id)
        )
        if failed_run is not None:
            failed_run.status = "FAILED"
            failed_run.completed_at = datetime.now(UTC)
            failed_run.error_message = str(exc)[:2000]
            session.commit()
        raise
