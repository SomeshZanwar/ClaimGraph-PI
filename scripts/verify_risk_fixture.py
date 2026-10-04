from sqlalchemy import select

from app.db.models import RiskSignal, RuleRun
from app.db.session import SessionLocal


def main() -> None:
    with SessionLocal() as session:
        latest_run = session.scalar(
            select(RuleRun).order_by(RuleRun.started_at.desc()).limit(1)
        )
        if latest_run is None:
            raise RuntimeError("No deterministic rule run found")

        signals = session.scalars(
            select(RiskSignal).where(RiskSignal.rule_run_id == latest_run.id)
        ).all()

        rule_ids = {signal.rule_id for signal in signals}

        if latest_run.status != "COMPLETED":
            raise RuntimeError(f"Rule run status is {latest_run.status}")

        if "CG-DUP-001" not in rule_ids:
            raise RuntimeError("Expected duplicate-claim fixture signal was not generated")

        if "CG-TEMP-001" not in rule_ids:
            raise RuntimeError("Expected rapid-repeat fixture signal was not generated")

        print(
            f"Verified rule run {latest_run.id}: "
            f"{len(signals)} signals across {len(rule_ids)} rule types"
        )


if __name__ == "__main__":
    main()
