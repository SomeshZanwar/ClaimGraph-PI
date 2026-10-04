from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError, VerifyMismatchError
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import AuthToken, User, UserSession

_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def validate_password(password: str, email: str | None = None) -> None:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    if len(password) > 128:
        raise ValueError("Password must contain at most 128 characters")

    if email:
        local_part = normalize_email(email).split("@", maxsplit=1)[0]
        if local_part and len(local_part) >= 4 and local_part in password.casefold():
            raise ValueError("Password must not contain the email username")


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _password_hasher.check_needs_rehash(password_hash)


def generate_secret_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_identifier(value: str) -> str:
    settings = get_settings()
    return hmac.new(
        settings.session_secret.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def issue_auth_token(
    session: Session,
    *,
    user: User,
    token_type: str,
    ttl_minutes: int | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)

    session.execute(
        update(AuthToken)
        .where(
            AuthToken.user_id == user.id,
            AuthToken.token_type == token_type,
            AuthToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_token = generate_secret_token()
    session.add(
        AuthToken(
            user_id=user.id,
            token_type=token_type,
            token_hash=hash_token(raw_token),
            created_at=now,
            expires_at=now
            + timedelta(minutes=ttl_minutes or settings.auth_token_ttl_minutes),
        )
    )
    session.flush()
    return raw_token


def consume_auth_token(
    session: Session,
    *,
    raw_token: str,
    token_type: str,
) -> User | None:
    now = datetime.now(UTC)
    token = session.scalar(
        select(AuthToken).where(
            AuthToken.token_hash == hash_token(raw_token),
            AuthToken.token_type == token_type,
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > now,
        )
    )
    if token is None:
        return None

    user = session.get(User, token.user_id)
    if user is None or not user.is_active:
        return None

    token.used_at = now
    return user


def create_user_session(
    session: Session,
    *,
    user: User,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[UserSession, str, str]:
    settings = get_settings()
    now = datetime.now(UTC)
    raw_session_token = generate_secret_token()
    raw_csrf_token = generate_secret_token()

    user_session = UserSession(
        user_id=user.id,
        token_hash=hash_token(raw_session_token),
        csrf_token_hash=hash_token(raw_csrf_token),
        created_at=now,
        expires_at=now + timedelta(minutes=settings.session_ttl_minutes),
        last_seen_at=now,
        ip_hash=hash_identifier(ip_address) if ip_address else None,
        user_agent=(user_agent or "")[:512] or None,
    )
    session.add(user_session)
    session.flush()
    return user_session, raw_session_token, raw_csrf_token


def resolve_session(
    session: Session,
    *,
    raw_session_token: str,
) -> tuple[UserSession, User] | None:
    now = datetime.now(UTC)
    user_session = session.scalar(
        select(UserSession).where(
            UserSession.token_hash == hash_token(raw_session_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
    )
    if user_session is None:
        return None

    user = session.get(User, user_session.user_id)
    if user is None or not user.is_active:
        return None

    if (now - user_session.last_seen_at).total_seconds() >= 300:
        user_session.last_seen_at = now

    return user_session, user


def revoke_session(user_session: UserSession) -> None:
    if user_session.revoked_at is None:
        user_session.revoked_at = datetime.now(UTC)


def revoke_all_sessions(session: Session, user_id: object) -> None:
    session.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )
