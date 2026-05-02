from __future__ import annotations

import re

import pandas as pd


REQUIRED_COLUMNS = {
    "name",
    "email",
    "region",
    "reporting_period",
    "total_sales",
    "order_count",
    "status",
}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def _normalize_required_text(raw_value: object, *, field_name: str, csv_line: int) -> str:
    if pd.isna(raw_value):
        raise ValueError(f"row {csv_line}: {field_name} is empty")

    value = str(raw_value).strip()
    if not value:
        raise ValueError(f"row {csv_line}: {field_name} is empty")

    return value


def normalize_total_sales(raw_total_sales: object) -> float:
    if pd.isna(raw_total_sales):
        raise ValueError("total_sales is empty")

    normalized = str(raw_total_sales).strip().replace(",", "")

    try:
        total_sales = float(normalized)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"invalid total_sales value: {raw_total_sales!r}") from exc

    if total_sales < 0:
        raise ValueError("total_sales must be greater than or equal to zero")

    return total_sales


def normalize_order_count(raw_order_count: object) -> int:
    if pd.isna(raw_order_count):
        raise ValueError("order_count is empty")

    normalized = str(raw_order_count).strip().replace(",", "")
    if not normalized:
        raise ValueError("order_count is empty")

    try:
        numeric_value = float(normalized)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"invalid order_count value: {raw_order_count!r}") from exc

    if not numeric_value.is_integer():
        raise ValueError("order_count must be a whole number")

    order_count = int(numeric_value)
    if order_count < 0:
        raise ValueError("order_count must be greater than or equal to zero")

    return order_count


def validate_row(row: pd.Series, csv_line: int) -> tuple[str, str, str, str, float, int, str]:
    name = _normalize_required_text(row["name"], field_name="name", csv_line=csv_line)

    raw_email = row["email"]
    if pd.isna(raw_email):
        raise ValueError(f"row {csv_line}: email is empty")
    email = str(raw_email).strip().lower()
    if not validate_email(email):
        raise ValueError(f"row {csv_line}: invalid email {email!r}")

    region = _normalize_required_text(row["region"], field_name="region", csv_line=csv_line)
    reporting_period = _normalize_required_text(
        row["reporting_period"],
        field_name="reporting_period",
        csv_line=csv_line,
    )
    try:
        total_sales = normalize_total_sales(row["total_sales"])
    except ValueError as exc:
        raise ValueError(f"row {csv_line}: {exc}") from exc

    try:
        order_count = normalize_order_count(row["order_count"])
    except ValueError as exc:
        raise ValueError(f"row {csv_line}: {exc}") from exc

    status = _normalize_required_text(row["status"], field_name="status", csv_line=csv_line)

    return name, email, region, reporting_period, total_sales, order_count, status
