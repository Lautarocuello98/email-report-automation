from __future__ import annotations

from pathlib import Path

import pandas as pd

from .email_sender import log_email_result, send_email
from .report_generator import generate_report, load_email_template
from .validation import REQUIRED_COLUMNS, validate_row


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
            name, email, sales = validate_row(row=row, csv_line=csv_line)
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
