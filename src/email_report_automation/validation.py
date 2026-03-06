from __future__ import annotations

import re

import pandas as pd


REQUIRED_COLUMNS = {"name", "email", "sales"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def normalize_sales(raw_sales: object) -> float:
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


def validate_row(row: pd.Series, csv_line: int) -> tuple[str, str, float]:
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
    if not validate_email(email):
        raise ValueError(f"row {csv_line}: invalid email {email!r}")

    sales = normalize_sales(raw_sales)
    return name, email, sales
