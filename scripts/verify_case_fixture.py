from app.db.models import CaseEvidence, InvestigationCase
from app.db.session import SessionLocal
from sqlalchemy import func, select


def main() -> None:
    with SessionLocal() as session:
        cases = session.scalars(
            select(InvestigationCase).order_by(
                InvestigationCase.priority_score.desc()
            )
        ).all()

        if not cases:
            raise RuntimeError("Expected at least one investigation case")

        for case in cases:
            evidence_count = session.scalar(
                select(func.count())
                .select_from(CaseEvidence)
                .where(CaseEvidence.case_id == case.id)
            )
            if not evidence_count:
                raise RuntimeError(f"Case {case.case_key} has no evidence")

            evidence = session.scalar(
                select(CaseEvidence)
                .where(
                    CaseEvidence.case_id == case.id,
                    CaseEvidence.evidence_hash == case.current_evidence_hash,
                )
                .limit(1)
            )
            if evidence is None:
                raise RuntimeError(
                    f"Case {case.case_key} current evidence hash is unresolved"
                )

            priority = evidence.payload.get("priority", {})
            note = str(priority.get("note", ""))
            if "not a fraud probability" not in note:
                raise RuntimeError(
                    f"Case {case.case_key} is missing priority-score boundary text"
                )

        print(f"Verified {len(cases)} investigation cases with evidence")


if __name__ == "__main__":
    main()
