import pytest
from openpyxl import load_workbook

from email_report_automation.report_generator import _slugify, format_currency, generate_report, load_email_template


def test_slugify_removes_unsafe_characters() -> None:
    assert _slugify(" John Doe ") == "john_doe"
    assert _slugify("Client / Name #1") == "client_name_1"
    assert _slugify("___") == "client"


def test_load_email_template_reads_file(local_tmp_dir) -> None:
    template = local_tmp_dir / "template.txt"
    template.write_text("Hello {name}", encoding="utf-8")

    assert load_email_template(template) == "Hello {name}"


def test_load_email_template_raises_for_missing_file(local_tmp_dir) -> None:
    with pytest.raises(FileNotFoundError):
        load_email_template(local_tmp_dir / "missing.txt")


def test_format_currency_returns_dollar_string() -> None:
    assert format_currency(1200.5) == "$1,200.50"


def test_generate_report_creates_excel_file(local_tmp_dir) -> None:
    report = generate_report(
        name="John Doe",
        email="john.doe@example.com",
        region="North America",
        reporting_period="Q1 2026",
        total_sales=1200.5,
        order_count=12,
        status="Active",
        output_dir=local_tmp_dir,
    )

    assert report.exists()
    assert report.name.startswith("report_john_doe_johndoe")

    workbook = load_workbook(report)
    worksheet = workbook["Report"]

    assert worksheet["A1"].value == "Client Sales Report"
    assert worksheet["B4"].value == "John Doe"
    assert worksheet["B5"].value == "john.doe@example.com"
    assert worksheet["B6"].value == "North America"
    assert worksheet["B7"].value == "Q1 2026"
    assert worksheet["B8"].value == 1200.5
    assert worksheet["B8"].number_format == "$#,##0.00"
    assert worksheet["B9"].value == 12
    assert worksheet["B10"].value == "Active"
