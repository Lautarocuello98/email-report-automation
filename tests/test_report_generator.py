import pandas as pd
import pytest

from report_generator import _slugify, generate_report, load_email_template


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


def test_generate_report_creates_excel_file(local_tmp_dir) -> None:
    report = generate_report(
        name="John Doe",
        email="john.doe@example.com",
        sales=1200.5,
        output_dir=local_tmp_dir,
    )

    assert report.exists()
    assert report.name.startswith("report_john_doe_johndoe")

    df = pd.read_excel(report)
    assert list(df["Field"]) == ["Client Name", "Email", "Sales"]
    assert df.loc[0, "Value"] == "John Doe"
    assert df.loc[1, "Value"] == "john.doe@example.com"
    assert df.loc[2, "Value"] == "1,200.50"
