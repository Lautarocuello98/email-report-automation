from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


FILENAME_PATTERN = re.compile(r"[^a-z0-9_-]+")
REPEATED_SEPARATOR_PATTERN = re.compile(r"[_-]{2,}")


def load_email_template(template_path: Path) -> str:
    """Load the email template from a text file."""
    if not template_path.is_file():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def _slugify(value: str) -> str:
    slug = value.strip().lower().replace(" ", "_")
    slug = FILENAME_PATTERN.sub("", slug)
    slug = REPEATED_SEPARATOR_PATTERN.sub("_", slug)
    slug = slug.strip("_-")
    return slug or "client"


def generate_report(name: str, email: str, sales: float, output_dir: Path) -> Path:
    """Generate a simple Excel report for one client."""
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _slugify(name)
    safe_email = _slugify(email.split("@", maxsplit=1)[0])
    report_path = output_dir / f"report_{safe_name}_{safe_email}.xlsx"

    report_data = pd.DataFrame(
        [
            {"Field": "Client Name", "Value": name},
            {"Field": "Email", "Value": email},
            {"Field": "Sales", "Value": f"{sales:,.2f}"},
        ]
    )

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        report_data.to_excel(writer, index=False, sheet_name="Report")
        worksheet = writer.sheets["Report"]
        worksheet.column_dimensions["A"].width = 20
        worksheet.column_dimensions["B"].width = 32

    return report_path
