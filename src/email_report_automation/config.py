from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


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


def load_environment(env_file: Path | None = None, *, override: bool = False) -> None:
    """Load environment variables from a .env file without side effects on import."""
    target = env_file if env_file is not None else DEFAULT_ENV_FILE
    load_dotenv(dotenv_path=target, override=override)


def load_smtp_settings() -> SMTPSettings:
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
