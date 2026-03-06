from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from email_sender import log_email_result, send_email
from report_generator import generate_report, load_email_template


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = BASE_DIR / "data" / "clients.csv"
DEFAULT_TEMPLATE_FILE = BASE_DIR / "templates" / "email_template.txt"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output" / "reports"
DEFAULT_LOG_FILE = BASE_DIR / "logs" / "email_log.txt"

REQUIRED_COLUMNS = {"name", "email", "sales"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Automate client sales reports by email.")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE, help="Path to clients CSV file.")
    parser.add_argument(
        "--template-file",
        type=Path,
        default=DEFAULT_TEMPLATE_FILE,
        help="Path to email template text file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where generated reports are stored.",
    )
    parser.add_argument("--log-file", type=Path, default=DEFAULT_LOG_FILE, help="Path to execution log file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate reports and logs without sending real emails.",
    )
    return parser.parse_args()


def _validate_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def _normalize_sales(raw_sales: object) -> float:
    if pd.isna(raw_sales):
        raise ValueError("sales is empty")

    normalized = str(raw_sales).strip().replace(",", "")

    try:
        sales = float(normalized)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"invalid sales value: {raw_sales!r}") from exc

    if sales < 0:
        raise ValueError("sales must be greater than or equal to zero")

    return sales


def _validate_row(row: pd.Series, csv_line: int) -> tuple[str, str, float]:
    raw_name = row["name"]
    raw_email = row["email"]
    raw_sales = row["sales"]

    if pd.isna(raw_name):
        raise ValueError(f"row {csv_line}: name is empty")
    name = str(raw_name).strip()
    if not name:
        raise ValueError(f"row {csv_line}: name is empty")

    if pd.isna(raw_email):
        raise ValueError(f"row {csv_line}: email is empty")
    email = str(raw_email).strip().lower()
    if not _validate_email(email):
        raise ValueError(f"row {csv_line}: invalid email {email!r}")

    sales = _normalize_sales(raw_sales)
    return name, email, sales


def run_workflow(
    *,
    data_file: Path,
    template_file: Path,
    output_dir: Path,
    log_file: Path,
    dry_run: bool,
) -> int:
    """Run the full email report automation workflow."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"Data file not found: {data_file}")
        return 1
    except Exception as exc:
        print(f"Failed to read CSV file {data_file}: {exc}")
        return 1

    if not REQUIRED_COLUMNS.issubset(df.columns):
        print(
            "CSV is missing required columns. "
            f"Expected: {sorted(REQUIRED_COLUMNS)}, Found: {sorted(df.columns)}"
        )
        return 1

    try:
        template = load_email_template(template_file)
    except FileNotFoundError as exc:
        print(exc)
        return 1
    except Exception as exc:
        print(f"Failed to read email template {template_file}: {exc}")
        return 1

    sent_count = 0
    failed_count = 0
    skipped_count = 0

    for row_index, row in df.iterrows():
        csv_line = row_index + 2
        try:
            name, email, sales = _validate_row(row=row, csv_line=csv_line)
        except ValueError as exc:
            skipped_count += 1
            log_email_result(log_file, f"row-{csv_line}", f"SKIPPED - {exc}")
            print(f"Skipping row {csv_line}: {exc}")
            continue

        try:
            report_path = generate_report(
                name=name,
                email=email,
                sales=sales,
                output_dir=output_dir,
            )
            formatted_sales = f"{sales:,.2f}"
            email_body = template.format(name=name, sales=formatted_sales)

            if dry_run:
                log_email_result(log_file, email, "DRY_RUN - EMAIL_NOT_SENT")
                print(f"[DRY RUN] Prepared email for {name} ({email}) with report {report_path.name}")
            else:
                send_email(
                    recipient=email,
                    subject=f"Sales Report for {name}",
                    body=email_body,
                    attachment_path=report_path,
                )
                log_email_result(log_file, email, "SENT")
                print(f"Email sent to {name} ({email})")

            sent_count += 1
        except KeyError as exc:
            failed_count += 1
            detail = f"FAILED - Missing template placeholder: {exc}"
            log_email_result(log_file, email, detail)
            print(f"Failed to process {name} ({email}): {detail}")
        except Exception as exc:
            failed_count += 1
            log_email_result(log_file, email, f"FAILED - {exc}")
            print(f"Failed to process {name} ({email}): {exc}")

    print(
        "Execution summary | "
        f"processed={len(df)} | sent_or_prepared={sent_count} | skipped={skipped_count} | failed={failed_count}"
    )
    return 0 if failed_count == 0 else 1


def main() -> int:
    args = parse_args()
    return run_workflow(
        data_file=args.data_file,
        template_file=args.template_file,
        output_dir=args.output_dir,
        log_file=args.log_file,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
