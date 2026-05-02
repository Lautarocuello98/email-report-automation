from __future__ import annotations

from pathlib import Path

from email_report_automation.workflow import run_workflow


def test_run_workflow_skips_invalid_email_and_generates_only_valid_report(local_tmp_dir: Path) -> None:
    data_file = local_tmp_dir / "clients.csv"
    template_file = local_tmp_dir / "email_template.txt"
    output_dir = local_tmp_dir / "reports"
    log_file = local_tmp_dir / "logs" / "email_log.txt"

    data_file.write_text(
        "\n".join(
            [
                "name,email,region,reporting_period,total_sales,order_count,status",
                "John Doe,john@example.com,North America,Q1 2026,1200.50,10,Active",
                "Jane Doe,invalid-email,Europe,Q1 2026,900.00,8,Pending Review",
            ]
        ),
        encoding="utf-8",
    )
    template_file.write_text(
        "Hello {name}, report for {reporting_period}: {total_sales}",
        encoding="utf-8",
    )

    exit_code = run_workflow(
        data_file=data_file,
        template_file=template_file,
        output_dir=output_dir,
        log_file=log_file,
        dry_run=True,
    )

    assert exit_code == 0
    generated_reports = sorted(output_dir.glob("*.xlsx"))
    assert len(generated_reports) == 1
    assert generated_reports[0].name.startswith("report_john_doe_john")

    log_contents = log_file.read_text(encoding="utf-8")
    assert "john@example.com | DRY_RUN - EMAIL_NOT_SENT" in log_contents
    assert "row-3 | SKIPPED - row 3: invalid email 'invalid-email'" in log_contents
