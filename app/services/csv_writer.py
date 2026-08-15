import csv
from pathlib import Path
from typing import Iterable

from app.models.transaction import Transaction


EXPORT_HEADERS = [
    "transaction_id",
    "transaction_date",
    "description",
    "amount",
    "merchant",
    "category",
    "confidence",
]


def export_transactions(
    transactions: Iterable[Transaction], filepath: str | Path
) -> Path:
    output_path = Path(filepath)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EXPORT_HEADERS)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(
                {
                    "transaction_id": transaction.transaction_id,
                    "transaction_date": transaction.transaction_date.isoformat(),
                    "description": transaction.description,
                    "amount": str(transaction.amount),
                    "merchant": transaction.merchant or "",
                    "category": transaction.category,
                    "confidence": f"{transaction.confidence:.1f}",
                }
            )
    return output_path
