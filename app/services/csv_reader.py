import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO

from app.db.models import Statement, Transaction


STANDARD_HEADERS = {"description", "transaction_date", "amount"}
CHASE_HEADERS = {"Posting Date", "Description", "Amount"}


class CSVImportError(ValueError):
    pass


class CSVReader:
    """Read a supported statement CSV and build unsaved database objects."""

    def read(self, file: TextIO, statement: Statement) -> list[Transaction]:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise CSVImportError("The CSV is empty or does not contain headers.")

        headers = set(reader.fieldnames)
        if STANDARD_HEADERS.issubset(headers):
            date_header = "transaction_date"
            description_header = "description"
            amount_header = "amount"
        elif CHASE_HEADERS.issubset(headers):
            date_header = "Posting Date"
            description_header = "Description"
            amount_header = "Amount"
        else:
            raise CSVImportError(
                "Unsupported CSV headers. Include description, transaction_date, "
                "and amount, or use a Chase activity export."
            )

        transactions = []
        for row_number, row in enumerate(reader, start=1):
            description = (row.get(description_header) or "").strip()
            if not description:
                raise CSVImportError(
                    f"Transaction description is required on row {row_number + 1}."
                )

            transaction = Transaction(
                statement=statement,
                source_row_number=row_number,
                transaction_date=self._parse_date(row.get(date_header), row_number),
                description=description,
                normalized_description="",
                amount=self._parse_amount(row.get(amount_header), row_number),
                classification_status="unclassified",
            )
            transactions.append(transaction)

        return transactions

    def read_path(self, path: str | Path, statement: Statement) -> list[Transaction]:
        with open(path, encoding="utf-8-sig", newline="") as file:
            return self.read(file, statement)

    def _parse_date(self, value: str | None, row_number: int):
        if not value:
            raise CSVImportError(
                f"Transaction date is required on row {row_number + 1}."
            )

        for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(value.strip(), date_format).date()
            except ValueError:
                pass

        raise CSVImportError(
            f"Invalid transaction date {value!r} on row {row_number + 1}."
        )

    def _parse_amount(self, value: str | None, row_number: int) -> Decimal:
        if not value:
            raise CSVImportError(
                f"Transaction amount is required on row {row_number + 1}."
            )

        cleaned = value.strip().replace("$", "").replace(",", "")
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]

        try:
            return Decimal(cleaned)
        except InvalidOperation as error:
            raise CSVImportError(
                f"Invalid transaction amount {value!r} on row {row_number + 1}."
            ) from error
