from pathlib import Path
import pandas as pd


def load_email_template(template_path: Path) -> str:
    """Load the email template from a text file."""
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_path}")


def generate_report(name: str, email: str, sales, output_dir: Path) -> Path:
    """Generate a simple Excel report for one client."""
    safe_name = name.lower().replace(" ", "_")
    report_path = output_dir / f"report_{safe_name}.xlsx"

    report_data = pd.DataFrame(
        [
            {"Field": "Client Name", "Value": name},
            {"Field": "Email", "Value": email},
            {"Field": "Sales", "Value": sales},
        ]
    )

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        report_data.to_excel(writer, index=False, sheet_name="Report")

    return report_path