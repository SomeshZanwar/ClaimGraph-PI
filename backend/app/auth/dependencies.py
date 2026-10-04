from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import User, UserSession
from app.db.session import get_db
from app.auth.security import hash_token, resolve_session


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: UserSession


def get_auth_context(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> AuthContext:
    settings = get_settings()
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    resolved = resolve_session(db, raw_session_token=raw_token)
    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired",
        )

    user_session, user = resolved
    return AuthContext(user=user, session=user_session)


def enforce_csrf(request: Request, context: AuthContext) -> None:
    settings = get_settings()
    header_token = request.headers.get("X-CSRF-Token")
    cookie_token = request.cookies.get(settings.csrf_cookie_name)

    if (
        not header_token
        or not cookie_token
        or header_token != cookie_token
        or hash_token(header_token) != context.session.csrf_token_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )


def require_roles(*allowed_roles: str):
    def dependency(
        context: Annotated[AuthContext, Depends(get_auth_context)],
    ) -> AuthContext:
        if context.user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return context

    return dependency
