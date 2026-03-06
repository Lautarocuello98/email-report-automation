from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


@dataclass(frozen=True)
class SMTPSettings:
    sender_email: str
    sender_password: str
    server: str
    port: int
    use_starttls: bool
    timeout_seconds: int


def _to_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_smtp_settings() -> SMTPSettings:
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    server = os.getenv("SMTP_SERVER")
    port_raw = os.getenv("SMTP_PORT")

    missing = [
        key
        for key, value in {
            "EMAIL_ADDRESS": sender_email,
            "EMAIL_PASSWORD": sender_password,
            "SMTP_SERVER": server,
            "SMTP_PORT": port_raw,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing email configuration in .env file: {', '.join(missing)}")

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("SMTP_PORT must be a valid integer") from exc
    if port < 1 or port > 65535:
        raise ValueError("SMTP_PORT must be between 1 and 65535")

    timeout_raw = os.getenv("SMTP_TIMEOUT_SECONDS", "30")
    try:
        timeout_seconds = int(timeout_raw)
    except ValueError as exc:
        raise ValueError("SMTP_TIMEOUT_SECONDS must be a valid integer") from exc
    if timeout_seconds < 1:
        raise ValueError("SMTP_TIMEOUT_SECONDS must be greater than zero")

    use_starttls = _to_bool(os.getenv("SMTP_USE_STARTTLS"), default=port != 465)

    return SMTPSettings(
        sender_email=sender_email,
        sender_password=sender_password,
        server=server,
        port=port,
        use_starttls=use_starttls,
        timeout_seconds=timeout_seconds,
    )


def send_email(recipient: str, subject: str, body: str, attachment_path: Path) -> None:
    """Send an email with an attachment using SMTP."""
    if not attachment_path.is_file():
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    settings = _load_smtp_settings()

    msg = EmailMessage()
    msg["From"] = settings.sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with attachment_path.open("rb") as file:
        file_data = file.read()

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=attachment_path.name,
    )

    if settings.port == 465 and not settings.use_starttls:
        with smtplib.SMTP_SSL(settings.server, settings.port, timeout=settings.timeout_seconds) as server:
            server.login(settings.sender_email, settings.sender_password)
            server.send_message(msg)
        return

    with smtplib.SMTP(settings.server, settings.port, timeout=settings.timeout_seconds) as server:
        server.ehlo()
        if settings.use_starttls:
            server.starttls()
            server.ehlo()
        server.login(settings.sender_email, settings.sender_password)
        server.send_message(msg)


def log_email_result(log_file: Path, recipient: str, status: str) -> None:
    """Append the email sending result to a log file."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {recipient} | {status}\n")
