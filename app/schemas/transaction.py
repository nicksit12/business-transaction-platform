from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Transaction:
    """A normalized financial transaction."""

    transaction_id: int
    description: str
    transaction_date: date
    amount: Decimal
    category: str = "Unclassified"
    merchant: str | None = None
    confidence: float = 0.0
