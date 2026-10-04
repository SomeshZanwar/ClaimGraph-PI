from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.auth import routes
from app.auth.rate_limit import RateLimitExceeded
from app.auth.security import hash_password, verify_password
from app.db.models import AuthToken, User, UserSession
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_auth_tables() -> None:
    with SessionLocal() as session:
        session.execute(delete(AuthToken))
        session.execute(delete(UserSession))
        session.execute(delete(User))
        session.commit()


def test_argon2_password_round_trip() -> None:
    password_hash = hash_password("a-long-secure-password-123")

    assert verify_password("a-long-secure-password-123", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_signup_verify_login_me_and_csrf_logout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = f"investigator-{uuid4().hex}@example.com"
    password = "SecureExamplePassword123!"
    captured: dict[str, str] = {}

    monkeypatch.setattr(routes, "_rate_limit", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        routes,
        "send_verification_email",
        lambda _email, token: captured.__setitem__("verify_token", token),
    )

    signup = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password},
    )
    assert signup.status_code == 202
    assert "verify_token" in captured

    verify = client.post(
        "/api/v1/auth/verify-email",
        json={"token": captured["verify_token"]},
    )
    assert verify.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "INVESTIGATOR"
    assert login.json()["user"]["email_verified"] is True

    csrf_token = client.cookies.get("cg_csrf")
    assert csrf_token
    assert client.cookies.get("cg_session")

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == email

    missing_csrf = client.post("/api/v1/auth/logout")
    assert missing_csrf.status_code == 403

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 200

    after_logout = client.get("/api/v1/auth/me")
    assert after_logout.status_code == 401


def test_password_reset_revokes_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = f"reset-{uuid4().hex}@example.com"
    old_password = "OriginalSecurePassword123!"
    new_password = "ReplacementSecurePassword456!"
    captured: dict[str, str] = {}

    monkeypatch.setattr(routes, "_rate_limit", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        routes,
        "send_verification_email",
        lambda _email, token: captured.__setitem__("verify_token", token),
    )
    monkeypatch.setattr(
        routes,
        "send_password_reset_email",
        lambda _email, token: captured.__setitem__("reset_token", token),
    )

    assert client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": old_password},
    ).status_code == 202
    assert client.post(
        "/api/v1/auth/verify-email",
        json={"token": captured["verify_token"]},
    ).status_code == 200
    assert client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    ).status_code == 200

    reset_request = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": email},
    )
    assert reset_request.status_code == 200
    assert "reset_token" in captured

    reset_confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": captured["reset_token"],
            "new_password": new_password,
        },
    )
    assert reset_confirm.status_code == 200

    assert client.get("/api/v1/auth/me").status_code == 401

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    assert new_login.status_code == 200


def test_login_rate_limit_maps_to_http_429(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def blocked(*_args, **_kwargs) -> None:
        raise RateLimitExceeded(42)

    monkeypatch.setattr(routes, "enforce_rate_limit", blocked)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "limited@example.com",
            "password": "any-password",
        },
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "42"


def test_existing_verified_email_does_not_disclose_registration_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = f"existing-{uuid4().hex}@example.com"
    monkeypatch.setattr(routes, "_rate_limit", lambda *_args, **_kwargs: None)

    with SessionLocal() as session:
        from datetime import UTC, datetime

        user = User(
            email=email,
            email_normalized=email.casefold(),
            password_hash=hash_password("ExistingSecurePassword123!"),
            role="INVESTIGATOR",
            is_active=True,
            email_verified_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(user)
        session.commit()

    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": "DifferentSecurePassword123!",
        },
    )

    assert response.status_code == 202
    assert "verification instructions" in response.json()["message"].lower()
