from app.db.session import SessionLocal
from app.risk.engine import load_rule_definitions, run_rules


def main() -> None:
    rules = load_rule_definitions()

    with SessionLocal() as session:
        run = run_rules(session, rules)

    print(f"Rule run: {run.id}")
    print(f"Ruleset hash: {run.ruleset_hash}")
    print(f"Status: {run.status}")
    print(f"Signals generated: {run.signal_count}")


if __name__ == "__main__":
    main()
