from pathlib import Path
import pandas as pd

from report_generator import generate_report, load_email_template
from email_sender import send_email, log_email_result


DATA_FILE = Path("data/clients.csv")
TEMPLATE_FILE = Path("templates/email_template.txt")
OUTPUT_DIR = Path("output/reports")
LOG_FILE = Path("logs/email_log.txt")


def main():
    """Run the full email report automation workflow."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"Data file not found: {DATA_FILE}")
        return
    except Exception as exc:
        print(f"Failed to read CSV file: {exc}")
        return

    required_columns = {"name", "email", "sales"}
    if not required_columns.issubset(df.columns):
        print(
            "CSV is missing required columns. "
            f"Expected: {required_columns}, Found: {set(df.columns)}"
        )
        return

    template = load_email_template(TEMPLATE_FILE)

    for _, row in df.iterrows():
        name = str(row["name"]).strip()
        email = str(row["email"]).strip()
        sales = row["sales"]

        try:
            report_path = generate_report(name=name, email=email, sales=sales, output_dir=OUTPUT_DIR)

            email_body = template.format(name=name, sales=sales)

            send_email(
                recipient=email,
                subject=f"Sales Report for {name}",
                body=email_body,
                attachment_path=report_path,
            )

            log_email_result(LOG_FILE, email, "SENT")
            print(f"Email sent to {name} ({email})")

        except Exception as exc:
            log_email_result(LOG_FILE, email, f"FAILED - {exc}")
            print(f"Failed to process {name} ({email}): {exc}")


if __name__ == "__main__":
    main()