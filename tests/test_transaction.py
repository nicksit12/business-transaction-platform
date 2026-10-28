from datetime import date
from decimal import Decimal

from app.db.models import Statement, Transaction


def test_transaction_database_model():
    statement = Statement(original_filename="test.csv", file_hash="hash")
    transaction = Transaction(
        statement=statement,
        source_row_number=1,
        transaction_date=date(2026, 3, 3),
        description="HOME_DEPOT",
        normalized_description="home depot",
        amount=Decimal("100.20"),
        classification_status="unclassified",
    )

    assert transaction.statement is statement
    assert transaction.transaction_date == date(2026, 3, 3)
    assert transaction.amount == Decimal("100.20")
