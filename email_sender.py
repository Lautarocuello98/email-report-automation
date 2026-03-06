import os
import smtplib
from pathlib import Path
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


def send_email(recipient: str, subject: str, body: str, attachment_path: Path) -> None:
    """Send an email with an attachment using SMTP."""
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    if not all([sender_email, sender_password, smtp_server, smtp_port]):
        raise ValueError("Missing email configuration in .env file.")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with open(attachment_path, "rb") as file:
        file_data = file.read()
        file_name = attachment_path.name

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_name,
    )

    with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


def log_email_result(log_file: Path, recipient: str, status: str) -> None:
    """Append the email sending result to a log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {recipient} | {status}\n")