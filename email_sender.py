from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from email_report_automation.config import SMTPSettings, load_smtp_settings
from email_report_automation.email_sender import log_email_result, send_email

_load_smtp_settings = load_smtp_settings

__all__ = ["SMTPSettings", "load_smtp_settings", "_load_smtp_settings", "send_email", "log_email_result"]
