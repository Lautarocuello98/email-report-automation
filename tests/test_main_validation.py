import pandas as pd
import pytest

from email_report_automation.validation import normalize_order_count, normalize_total_sales, validate_row


def test_normalize_total_sales_accepts_numbers_and_comma_strings() -> None:
    assert normalize_total_sales(1200) == 1200.0
    assert normalize_total_sales("1,200.50") == 1200.5


def test_normalize_total_sales_rejects_negative_values() -> None:
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        normalize_total_sales(-1)


def test_normalize_order_count_accepts_integer_like_values() -> None:
    assert normalize_order_count(12) == 12
    assert normalize_order_count("18") == 18
    assert normalize_order_count("20.0") == 20


def test_normalize_order_count_rejects_fractional_values() -> None:
    with pytest.raises(ValueError, match="whole number"):
        normalize_order_count("10.5")


def test_validate_row_returns_clean_data() -> None:
    row = pd.Series(
        {
            "name": " John Doe ",
            "email": "JOHN@EXAMPLE.COM",
            "region": " North America ",
            "reporting_period": " Q1 2026 ",
            "total_sales": "1,000",
            "order_count": "15",
            "status": " Active ",
        }
    )
    name, email, region, reporting_period, total_sales, order_count, status = validate_row(
        row=row,
        csv_line=2,
    )

    assert name == "John Doe"
    assert email == "john@example.com"
    assert region == "North America"
    assert reporting_period == "Q1 2026"
    assert total_sales == 1000.0
    assert order_count == 15
    assert status == "Active"


def test_validate_row_rejects_invalid_email() -> None:
    row = pd.Series(
        {
            "name": "John",
            "email": "invalid-email",
            "region": "Europe",
            "reporting_period": "Q1 2026",
            "total_sales": "1000",
            "order_count": "10",
            "status": "Active",
        }
    )
    with pytest.raises(ValueError, match="invalid email"):
        validate_row(row=row, csv_line=2)


def test_validate_row_rejects_empty_name() -> None:
    row = pd.Series(
        {
            "name": "   ",
            "email": "john@example.com",
            "region": "Europe",
            "reporting_period": "Q1 2026",
            "total_sales": "1000",
            "order_count": "10",
            "status": "Active",
        }
    )
    with pytest.raises(ValueError, match="name is empty"):
        validate_row(row=row, csv_line=2)
