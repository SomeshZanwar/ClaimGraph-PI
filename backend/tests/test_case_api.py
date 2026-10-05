from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.auth.security import create_user_session, hash_password
from app.config import get_settings
from app.db.models import (
    AuthToken,
    CaseEvidence,
    CaseNote,
    InvestigationCase,
    User,
    UserSession,
)
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_case_auth_tables() -> None:
    client.cookies.clear()
    with SessionLocal() as session:
        session.execute(delete(CaseNote))
        session.execute(delete(CaseEvidence))
        session.execute(delete(InvestigationCase))
        session.execute(delete(AuthToken))
        session.execute(delete(UserSession))
        session.execute(delete(User))
        session.commit()


def create_user_and_session(role: str = "INVESTIGATOR") -> tuple[User, str, str]:
    now = datetime.now(UTC)
    with SessionLocal() as session:
        email = f"{uuid4().hex}@example.com"
        user = User(
            email=email,
            email_normalized=email.casefold(),
            password_hash=hash_password("SecurePasswordForApiTests123!"),
            role=role,
            is_active=True,
            email_verified_at=now,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.flush()
        user_session, raw_token, csrf = create_user_session(
            session,
            user=user,
            ip_address="127.0.0.1",
            user_agent="pytest",
        )
        session.commit()
        session.refresh(user)
        assert user_session.id
        return user, raw_token, csrf


def create_case(*, assigned_user_id=None) -> InvestigationCase:
    now = datetime.now(UTC)
    evidence_hash = "a" * 64
    with SessionLocal() as session:
        case = InvestigationCase(
            case_key=f"case-{uuid4().hex}",
            claim_record_id=str(uuid4()),
            status="NEW",
            priority_score=Decimal("63.00"),
            priority_band="HIGH",
            financial_exposure=Decimal("725.50"),
            strongest_signal="rules",
            assigned_user_id=assigned_user_id,
            current_evidence_hash=evidence_hash,
            created_at=now,
            updated_at=now,
        )
        session.add(case)
        session.flush()
        session.add(
            CaseEvidence(
                case_id=case.id,
                evidence_hash=evidence_hash,
                payload={
                    "providers": ["SYNNPI001"],
                    "rule_signals": [{"rule_id": "CG-DUP-001"}],
                    "financial_exposure": "725.50",
                },
                generated_at=now,
            )
        )
        session.commit()
        session.refresh(case)
        return case


def authenticate(raw_token: str, csrf: str) -> None:
    settings = get_settings()
    client.cookies.set(settings.session_cookie_name, raw_token)
    client.cookies.set(settings.csrf_cookie_name, csrf)


def test_unassigned_case_can_be_self_assigned_and_noted() -> None:
    user, raw_token, csrf = create_user_and_session()
    case = create_case()
    authenticate(raw_token, csrf)

    detail = client.get(f"/api/v1/cases/{case.id}")
    assert detail.status_code == 200

    missing_csrf = client.patch(
        f"/api/v1/cases/{case.id}",
        json={"assign_to_self": True},
    )
    assert missing_csrf.status_code == 403

    assigned = client.patch(
        f"/api/v1/cases/{case.id}",
        json={"assign_to_self": True, "status": "IN_REVIEW"},
        headers={"X-CSRF-Token": csrf},
    )
    assert assigned.status_code == 200
    assert assigned.json()["assigned_user_id"] == str(user.id)
    assert assigned.json()["status"] == "IN_REVIEW"

    note = client.post(
        f"/api/v1/cases/{case.id}/notes",
        json={"body": "Reviewed deterministic duplicate evidence."},
        headers={"X-CSRF-Token": csrf},
    )
    assert note.status_code == 201

    notes = client.get(f"/api/v1/cases/{case.id}/notes")
    assert notes.status_code == 200
    assert notes.json()[0]["body"] == "Reviewed deterministic duplicate evidence."


def test_cross_user_assigned_case_is_not_disclosed() -> None:
    owner, _owner_token, _owner_csrf = create_user_and_session()
    _other, other_token, other_csrf = create_user_and_session()
    case = create_case(assigned_user_id=owner.id)
    authenticate(other_token, other_csrf)

    response = client.get(f"/api/v1/cases/{case.id}")
    assert response.status_code == 404


def test_auditor_can_read_but_cannot_mutate() -> None:
    _auditor, raw_token, csrf = create_user_and_session(role="AUDITOR")
    case = create_case()
    authenticate(raw_token, csrf)

    assert client.get(f"/api/v1/cases/{case.id}").status_code == 200

    update = client.patch(
        f"/api/v1/cases/{case.id}",
        json={"assign_to_self": True},
        headers={"X-CSRF-Token": csrf},
    )
    assert update.status_code == 403
