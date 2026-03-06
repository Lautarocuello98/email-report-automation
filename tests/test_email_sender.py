import pytest

from email_report_automation.config import load_smtp_settings
from email_report_automation.email_sender import log_email_result


def _set_base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_ADDRESS", "sender@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")


def test_load_smtp_settings_with_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_base_env(monkeypatch)
    monkeypatch.delenv("SMTP_USE_STARTTLS", raising=False)
    monkeypatch.delenv("SMTP_TIMEOUT_SECONDS", raising=False)

    settings = load_smtp_settings()

    assert settings.sender_email == "sender@example.com"
    assert settings.server == "smtp.example.com"
    assert settings.port == 587
    assert settings.use_starttls is True
    assert settings.timeout_seconds == 30


def test_load_smtp_settings_rejects_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_base_env(monkeypatch)
    monkeypatch.setenv("SMTP_PORT", "not-a-number")

    with pytest.raises(ValueError, match="SMTP_PORT must be a valid integer"):
        load_smtp_settings()


def test_load_smtp_settings_requires_all_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    monkeypatch.delenv("SMTP_SERVER", raising=False)
    monkeypatch.delenv("SMTP_PORT", raising=False)

    with pytest.raises(ValueError, match="Missing email configuration"):
        load_smtp_settings()


def test_log_email_result_creates_parent_folder(local_tmp_dir) -> None:
    log_file = local_tmp_dir / "nested" / "email_log.txt"
    log_email_result(log_file=log_file, recipient="john@example.com", status="SENT")

    content = log_file.read_text(encoding="utf-8")
    assert "john@example.com" in content
    assert "SENT" in content
