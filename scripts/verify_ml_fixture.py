from app.db.models import ClaimModelScore, ModelRun
from app.db.session import SessionLocal
from sqlalchemy import func, select


def main() -> None:
    with SessionLocal() as session:
        latest_run = session.scalar(
            select(ModelRun).order_by(ModelRun.trained_at.desc()).limit(1)
        )
        if latest_run is None:
            raise RuntimeError("No model run found")
        if latest_run.status != "COMPLETED":
            raise RuntimeError(f"Model run status is {latest_run.status}")
        if latest_run.model_type != "IsolationForest":
            raise RuntimeError(f"Unexpected model type: {latest_run.model_type}")

        score_count = session.scalar(
            select(func.count())
            .select_from(ClaimModelScore)
            .where(ClaimModelScore.model_run_id == latest_run.id)
        )
        if score_count != latest_run.training_row_count:
            raise RuntimeError(
                "Persisted score count does not match training feature row count"
            )

        if latest_run.anomaly_threshold is None:
            raise RuntimeError("Model run has no anomaly threshold")

        print(
            f"Verified model {latest_run.model_version}: "
            f"{score_count} scored claims"
        )


if __name__ == "__main__":
    main()
