# Email Report Automation

Automate per-client sales report generation (Excel) and email delivery over SMTP.

This repository is portfolio-oriented: clear architecture, input validation, dry-run mode, structured logging, and automated tests.

## Table of contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Execution flow](#execution-flow)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Input format](#input-format)
- [Usage](#usage)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Recommended screenshots](#recommended-screenshots)
- [Roadmap](#roadmap)
- [License](#license)

## Overview

Starting from a clients CSV, the system:

1. validates each row (`name`, `email`, `sales`),
2. generates one `.xlsx` report per client,
3. renders an email body from a text template,
4. sends the email (or simulates with `--dry-run`),
5. logs each result.

## Architecture

The project is intentionally split into 3 focused modules:

- `main.py`: workflow orchestration, CLI arguments, row validation, and error handling.
- `report_generator.py`: template loading and per-client Excel report generation.
- `email_sender.py`: SMTP config loading from environment, email sending, and execution logging.

This separation keeps the code maintainable and testable.

## Execution flow

1. Parse CLI arguments (`--data-file`, `--template-file`, `--output-dir`, `--log-file`, `--dry-run`).
2. Load CSV and verify required columns.
3. Load email template.
4. For each valid row:
   - generate report in `output/reports/`,
   - render email body,
   - send email (or simulate),
   - write log entry.
5. Print final summary (`processed`, `sent_or_prepared`, `skipped`, `failed`).

## Requirements

- Python 3.10+
- Runtime dependencies:
  - `pandas==2.2.3`
  - `openpyxl==3.1.5`
  - `python-dotenv==1.0.1`
- Test dependencies:
  - `pytest==8.3.5`

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Configuration

1. Create `.env` from `.env.example`.
2. Fill in valid SMTP credentials.

Supported variables:

- `EMAIL_ADDRESS`: sender email.
- `EMAIL_PASSWORD`: password or app password.
- `SMTP_SERVER`: SMTP host.
- `SMTP_PORT`: SMTP port.
- `SMTP_USE_STARTTLS`: `true/false`.
  - Gmail recommended setup: `true` with port `587`.
  - Direct SSL setup: port `465` and `false`.
- `SMTP_TIMEOUT_SECONDS`: connection/send timeout.

Example:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_STARTTLS=true
SMTP_TIMEOUT_SECONDS=30
```

## Input format

Default input file: `data/clients.csv`

Required columns:

- `name`
- `email`
- `sales`

Example:

```csv
name,email,sales
John Doe,john@example.com,1200
Anna Smith,anna@example.com,950
Mark Lee,mark@example.com,1575
```

## Usage

Normal execution:

```powershell
python main.py
```

Dry run (no real emails sent):

```powershell
python main.py --dry-run
```

Show help:

```powershell
python main.py --help
```

Override default paths:

```powershell
python main.py --data-file data/clients.csv --template-file templates/email_template.txt --output-dir output/reports --log-file logs/email_log.txt
```

## Testing

```powershell
pytest
```

Current coverage includes:

- row validation and sales normalization,
- filename sanitization for reports,
- template loading,
- Excel report generation,
- SMTP configuration validation,
- logging behavior.

## Project structure

```text
email-report-automation/
|-- .env.example
|-- .gitignore
|-- LICENSE
|-- README.md
|-- email_sender.py
|-- main.py
|-- report_generator.py
|-- requirements.txt
|-- requirements-dev.txt
|-- pytest.ini
|-- data/
|   `-- clients.csv
|-- templates/
|   `-- email_template.txt
|-- logs/
|   `-- .gitkeep
|-- output/
|   `-- reports/
|       `-- .gitkeep
`-- tests/
    |-- conftest.py
    |-- test_email_sender.py
    |-- test_main_validation.py
    `-- test_report_generator.py
```

## Recommended screenshots

To make the README look stronger in your portfolio, include 4-6 screenshots:

1. Terminal run with `--dry-run` showing successful summary.
2. `output/reports/` folder with generated `.xlsx` files.
3. One opened Excel report showing formatted fields.
4. `pytest` output with all tests passing.
5. Code snapshot of module separation (`main.py`, `report_generator.py`, `email_sender.py`).
6. `README` top section and project tree (optional but good for first impression).

## Roadmap

- Export execution summary to JSON/CSV for auditing.
- Add optional HTML email template support.
- Add configurable retries for transient SMTP failures.
- Move configuration to a dedicated typed module (`config.py`).

## License

MIT
