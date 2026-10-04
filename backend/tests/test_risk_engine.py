from app.risk.engine import load_rule_definitions, ruleset_hash


def test_rule_definitions_have_unique_versioned_ids() -> None:
    rules = load_rule_definitions()
    keys = {(rule.id, rule.version) for rule in rules}

    assert len(rules) == 4
    assert len(keys) == len(rules)


def test_ruleset_hash_is_deterministic() -> None:
    rules = load_rule_definitions()

    assert ruleset_hash(rules) == ruleset_hash(rules)


def test_rules_do_not_describe_fraud_as_fact() -> None:
    rules = load_rule_definitions()

    for rule in rules:
        explanation = rule.explanation.lower()
        assert "is fraudulent" not in explanation
        assert "fraud confirmed" not in explanation
