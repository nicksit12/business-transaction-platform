import csv
from typing import TextIO

from app.db.models import Transaction


class CSVWriter:
    headers = [
        "transaction_id",
        "transaction_date",
        "description",
        "normalized_description",
        "amount",
        "merchant",
        "category",
        "classification_status",
        "confidence",
    ]

    def write(self, transactions: list[Transaction], output: TextIO) -> TextIO:
        writer = csv.DictWriter(output, fieldnames=self.headers)
        writer.writeheader()

        for transaction in transactions:
            writer.writerow(
                {
                    "transaction_id": transaction.id,
                    "transaction_date": transaction.transaction_date.isoformat(),
                    "description": transaction.description,
                    "normalized_description": transaction.normalized_description,
                    "amount": str(transaction.amount),
                    "merchant": (
                        transaction.merchant.canonical_name
                        if transaction.merchant
                        else ""
                    ),
                    "category": (
                        transaction.category.name if transaction.category else ""
                    ),
                    "classification_status": transaction.classification_status,
                    "confidence": (
                        transaction.classification_confidence
                        if transaction.classification_confidence is not None
                        else ""
                    ),
                }
            )

        return output
