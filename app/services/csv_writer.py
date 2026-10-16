import csv
from pathlib import Path
from typing import Iterable
from typing import TextIO

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
    transactions: Iterable[Transaction], output: TextIO
) -> TextIO:
    writer = csv.DictWriter(output, fieldnames=EXPORT_HEADERS)
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
    return output
