from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .config import load_environment
from .workflow import run_workflow


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "clients.csv"
DEFAULT_TEMPLATE_FILE = PROJECT_ROOT / "templates" / "email_template.txt"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "reports"
DEFAULT_LOG_FILE = PROJECT_ROOT / "logs" / "email_log.txt"
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Automate client sales reports by email.")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE, help="Path to clients CSV file.")
    parser.add_argument(
        "--template-file",
        type=Path,
        default=DEFAULT_TEMPLATE_FILE,
        help="Path to email template text file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where generated reports are stored.",
    )
    parser.add_argument("--log-file", type=Path, default=DEFAULT_LOG_FILE, help="Path to execution log file.")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE, help="Path to .env file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate reports and logs without sending real emails.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_environment(args.env_file)
    return run_workflow(
        data_file=args.data_file,
        template_file=args.template_file,
        output_dir=args.output_dir,
        log_file=args.log_file,
        dry_run=args.dry_run,
    )
