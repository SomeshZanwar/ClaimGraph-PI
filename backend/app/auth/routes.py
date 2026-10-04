from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import record_audit_event
from app.auth.dependencies import AuthContext, enforce_csrf, get_auth_context
from app.auth.email import send_password_reset_email, send_verification_email
from app.auth.rate_limit import RateLimitExceeded, enforce_rate_limit
from app.auth.schemas import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    ResetConfirmRequest,
    ResetRequest,
    SignupRequest,
    TokenRequest,
    UserResponse,
)
from app.auth.security import (
    consume_auth_token,
    create_user_session,
    hash_identifier,
    hash_password,
    issue_auth_token,
    normalize_email,
    password_needs_rehash,
    revoke_all_sessions,
    revoke_session,
    validate_password,
    verify_password,
)
from app.config import get_settings
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        email_verified=user.email_verified_at is not None,
    )


def _request_identity(request: Request, email: str) -> str:
    host = request.client.host if request.client else "unknown"
    return hash_identifier(f"{host}|{normalize_email(email)}")


def _rate_limit(request: Request, email: str, action: str) -> None:
    settings = get_settings()
    key = f"claimgraph:auth:{action}:{_request_identity(request, email)}"
    try:
        enforce_rate_limit(
            key,
            limit=settings.login_rate_limit_attempts,
            window_seconds=settings.login_rate_limit_window_seconds,
        )
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc


def _set_auth_cookies(
    response: Response,
    session_token: str,
    csrf_token: str,
) -> None:
    settings = get_settings()
    secure = settings.app_env.lower() in {"production", "staging"}

    response.set_cookie(
        settings.session_cookie_name,
        session_token,
        max_age=settings.session_ttl_minutes * 60,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=settings.session_ttl_minutes * 60,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")


@router.post(
    "/signup",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def signup(
    payload: SignupRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    email = str(payload.email)
    normalized = normalize_email(email)
    _rate_limit(request, normalized, "signup")

    existing = db.scalar(
        select(User).where(User.email_normalized == normalized)
    )
    if existing is not None:
        if existing.email_verified_at is None and existing.is_active:
            token = issue_auth_token(
                db,
                user=existing,
                token_type="VERIFY_EMAIL",
            )
            db.commit()
            send_verification_email(existing.email, token)
        return MessageResponse(
            message="If the account can be registered, verification instructions will be sent."
        )

    try:
        validate_password(payload.password, email)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    now = datetime.now(UTC)
    user = User(
        email=email.strip(),
        email_normalized=normalized,
        password_hash=hash_password(payload.password),
        role="INVESTIGATOR",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()

    token = issue_auth_token(
        db,
        user=user,
        token_type="VERIFY_EMAIL",
    )
    record_audit_event(
        db,
        event_type="AUTH_SIGNUP_CREATED",
        user_id=user.id,
        resource_type="USER",
        resource_id=str(user.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()

    send_verification_email(user.email, token)
    return MessageResponse(
        message="If the account can be registered, verification instructions will be sent."
    )


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(
    payload: ResetRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    email = str(payload.email)
    normalized = normalize_email(email)
    _rate_limit(request, normalized, "resend-verification")

    user = db.scalar(
        select(User).where(User.email_normalized == normalized)
    )
    if user is not None and user.is_active and user.email_verified_at is None:
        token = issue_auth_token(
            db,
            user=user,
            token_type="VERIFY_EMAIL",
        )
        db.commit()
        send_verification_email(user.email, token)

    return MessageResponse(
        message="If verification is available for the account, instructions will be sent."
    )


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    payload: TokenRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    user = consume_auth_token(
        db,
        raw_token=payload.token,
        token_type="VERIFY_EMAIL",
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is invalid or expired",
        )

    now = datetime.now(UTC)
    user.email_verified_at = user.email_verified_at or now
    user.updated_at = now
    record_audit_event(
        db,
        event_type="AUTH_EMAIL_VERIFIED",
        user_id=user.id,
        resource_type="USER",
        resource_id=str(user.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()

    return MessageResponse(message="Email verification completed.")


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    email = str(payload.email)
    normalized = normalize_email(email)
    _rate_limit(request, normalized, "login")

    user = db.scalar(
        select(User).where(User.email_normalized == normalized)
    )
    if user is None or not verify_password(
        payload.password,
        user.password_hash if user else "",
    ):
        record_audit_event(
            db,
            event_type="AUTH_LOGIN_FAILED",
            metadata={
                "identity_hash": _request_identity(request, normalized),
            },
            request_id=getattr(request.state, "request_id", None),
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
        user.updated_at = datetime.now(UTC)

    user_session, session_token, csrf_token = create_user_session(
        db,
        user=user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    record_audit_event(
        db,
        event_type="AUTH_LOGIN_SUCCEEDED",
        user_id=user.id,
        resource_type="SESSION",
        resource_id=str(user_session.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()

    _set_auth_cookies(response, session_token, csrf_token)
    return LoginResponse(user=_user_response(user))


@router.get("/me", response_model=UserResponse)
def me(
    context: Annotated[AuthContext, Depends(get_auth_context)],
) -> UserResponse:
    return _user_response(context.user)


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    enforce_csrf(request, context)
    revoke_session(context.session)
    record_audit_event(
        db,
        event_type="AUTH_LOGOUT",
        user_id=context.user.id,
        resource_type="SESSION",
        resource_id=str(context.session.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()
    _clear_auth_cookies(response)
    return MessageResponse(message="Logged out.")


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(
    payload: ResetRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    email = str(payload.email)
    normalized = normalize_email(email)
    _rate_limit(request, normalized, "password-reset")

    user = db.scalar(
        select(User).where(User.email_normalized == normalized)
    )
    if user is not None and user.is_active:
        token = issue_auth_token(
            db,
            user=user,
            token_type="PASSWORD_RESET",
        )
        db.commit()
        send_password_reset_email(user.email, token)

    return MessageResponse(
        message="If the account exists, password reset instructions will be sent."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(
    payload: ResetConfirmRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    user = consume_auth_token(
        db,
        raw_token=payload.token,
        token_type="PASSWORD_RESET",
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or expired",
        )

    try:
        validate_password(payload.new_password, user.email)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    now = datetime.now(UTC)
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = now
    revoke_all_sessions(db, user.id)
    record_audit_event(
        db,
        event_type="AUTH_PASSWORD_RESET",
        user_id=user.id,
        resource_type="USER",
        resource_id=str(user.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()

    return MessageResponse(message="Password reset completed.")
