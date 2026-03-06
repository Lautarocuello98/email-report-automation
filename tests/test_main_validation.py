import pandas as pd
import pytest

from main import _normalize_sales, _validate_row


def test_normalize_sales_accepts_numbers_and_comma_strings() -> None:
    assert _normalize_sales(1200) == 1200.0
    assert _normalize_sales("1,200.50") == 1200.5


def test_normalize_sales_rejects_negative_values() -> None:
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        _normalize_sales(-1)


def test_validate_row_returns_clean_data() -> None:
    row = pd.Series({"name": " John Doe ", "email": "JOHN@EXAMPLE.COM", "sales": "1000"})
    name, email, sales = _validate_row(row=row, csv_line=2)

    assert name == "John Doe"
    assert email == "john@example.com"
    assert sales == 1000.0


def test_validate_row_rejects_invalid_email() -> None:
    row = pd.Series({"name": "John", "email": "invalid-email", "sales": "1000"})
    with pytest.raises(ValueError, match="invalid email"):
        _validate_row(row=row, csv_line=2)


def test_validate_row_rejects_empty_name() -> None:
    row = pd.Series({"name": "   ", "email": "john@example.com", "sales": "1000"})
    with pytest.raises(ValueError, match="name is empty"):
        _validate_row(row=row, csv_line=2)
