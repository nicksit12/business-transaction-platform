import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import IO, Iterable

from app.schemas.transaction import Transaction



STANDARD_HEADERS = {
    "transaction_id",
    "description",
    "transaction_date",
    "amount",
    "category",
}
CHASE_HEADERS = {"Posting Date", "Description", "Amount"}




class CSVImportError(ValueError):
    """Raised when an input CSV cannot be converted into transactions."""


def read_csv_standard(filepath: str | Path) -> list[dict[str, str]]:
    with open(filepath, mode="r", encoding="utf-8-sig", newline="") as file:
        return read_csv(file)


def read_csv(file: IO[str]) -> list[dict[str, str]]:
    reader = csv.DictReader(file)
    if not reader.fieldnames:
        raise CSVImportError("The CSV is empty or does not contain a header row.")
    return [dict(row) for row in reader]


def _parse_amount(value: str) -> Decimal:
    if not isinstance(value, str) or not value.strip():
        raise CSVImportError("Transaction amount is required.")
    cleaned = value.strip().replace("$", "").replace(",", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise CSVImportError(f"Invalid transaction amount: {value!r}") from exc


def _parse_date(value: str):
    if not isinstance(value, str) or not value.strip():
        raise CSVImportError("Transaction date is required.")
    for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    raise CSVImportError(
        f"Invalid transaction date: {value!r}. Use YYYY-MM-DD or MM/DD/YYYY."
    )


def convert_to_datatypes(records: list[dict[str, str]]) -> list[dict]:
    """Convert records in the app's standard CSV format to typed values."""
    converted = []
    for row_number, record in enumerate(records, start=2):
        try:
            raw_id = record["transaction_id"]
            digits = "".join(character for character in raw_id if character.isdigit())
            if not digits:
                raise CSVImportError(f"Invalid transaction ID: {raw_id!r}")
            description = record["description"]
            if not isinstance(description, str) or not description.strip():
                raise CSVImportError("Transaction description is required.")
            converted.append(
                {
                    "transaction_id": int(digits),
                    "description": description.strip(),
                    "transaction_date": _parse_date(record["transaction_date"]),
                    "amount": _parse_amount(record["amount"]),
                    "category": record.get("category", "") or "Unclassified",
                }
            )
        except (KeyError, TypeError) as exc:
            raise CSVImportError(f"Invalid data on CSV row {row_number}: {exc}") from exc
    return converted


def _convert_chase_records(records: list[dict[str, str]]) -> list[dict]:
    converted = []
    for transaction_id, record in enumerate(records, start=1):
        description = record["Description"]
        if not isinstance(description, str) or not description.strip():
            raise CSVImportError("Transaction description is required.")
        converted.append(
            {
                "transaction_id": transaction_id,
                "description": description.strip(),
                "transaction_date": _parse_date(record["Posting Date"]),
                "amount": _parse_amount(record["Amount"]),
                "category": "Unclassified",
            }
        )
    return converted


def convert_to_transactions(records: Iterable[dict]) -> list[Transaction]:
    return [Transaction(**record) for record in records]



def transactions_from_records(records: list[dict[str, str]]) -> list[Transaction]:
    if not records:
        return []

    headers = set(records[0])
    if STANDARD_HEADERS.issubset(headers):
        converted = convert_to_datatypes(records)
    elif CHASE_HEADERS.issubset(headers):
        converted = _convert_chase_records(records)
    else:
        raise CSVImportError(
            "Unsupported CSV headers. Use the standard transaction format or a "
            "Chase activity export."
        )
    return convert_to_transactions(converted)


def import_transactions(filepath: str | Path) -> list[Transaction]:
    return transactions_from_records(read_csv_standard(filepath))








