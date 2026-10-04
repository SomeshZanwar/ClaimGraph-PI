from app.casework.composer import compose_cases
from app.db.session import SessionLocal


def main() -> None:
    with SessionLocal() as session:
        cases = compose_cases(session)

    print(f"Cases composed: {len(cases)}")
    for case in sorted(cases, key=lambda item: item.priority_score, reverse=True):
        print(
            f"{case.case_key} | {case.priority_band} | "
            f"{case.priority_score} | exposure={case.financial_exposure}"
        )


if __name__ == "__main__":
    main()
