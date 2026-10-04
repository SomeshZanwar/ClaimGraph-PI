from __future__ import annotations

import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from app.config import get_settings


def _send_email(*, recipient: str, subject: str, body: str) -> None:
    settings = get_settings()
    if settings.email_delivery_mode != "smtp":
        raise RuntimeError(
            "Email delivery is not configured for SMTP; refusing to discard auth email"
        )

    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=10) as smtp:
        if settings.mail_use_tls:
            smtp.starttls()
        if settings.mail_user and settings.mail_password:
            smtp.login(settings.mail_user, settings.mail_password)
        smtp.send_message(message)


def send_verification_email(email: str, token: str) -> None:
    settings = get_settings()
    query = urlencode({"token": token})
    link = f"{settings.frontend_base_url.rstrip('/')}/verify-email?{query}"
    _send_email(
        recipient=email,
        subject="Verify your ClaimGraph PI account",
        body=(
            "Verify your ClaimGraph PI account using the link below. "
            "The link expires automatically.\n\n"
            f"{link}\n"
        ),
    )


def send_password_reset_email(email: str, token: str) -> None:
    settings = get_settings()
    query = urlencode({"token": token})
    link = f"{settings.frontend_base_url.rstrip('/')}/reset-password?{query}"
    _send_email(
        recipient=email,
        subject="Reset your ClaimGraph PI password",
        body=(
            "A password reset was requested for your ClaimGraph PI account. "
            "Use the link below if you made this request. The link expires automatically.\n\n"
            f"{link}\n"
        ),
    )
