from __future__ import annotations

import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from .config import SMTPSettings, load_smtp_settings


def send_email(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: Path,
    smtp_settings: SMTPSettings | None = None,
) -> None:
    """Send an email with an attachment using SMTP."""
    if not attachment_path.is_file():
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    settings = smtp_settings or load_smtp_settings()

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
