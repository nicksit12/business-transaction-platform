import pytest
from decimal import Decimal
from datetime import date
from app.schemas.transaction import Transaction

def test_transaction_model():
    data = {"transaction_id": 1, "description": "HOME_DEPOT", "transaction_date":  date(2026, 3, 3), "amount": Decimal("100.20"), "category": "material"}
    transaction = Transaction(**data)

    assert transaction.transaction_id == 1 
    assert transaction.description == "HOME_DEPOT"
    assert transaction.transaction_date == date(2026,3,3)
    assert transaction.amount == Decimal("100.20")
    assert transaction.category == "material"

def test_date_is_instance():
    data = {"transaction_id": 1, "description": "HOME_DEPOT", "transaction_date":  date(2026, 3, 3), "amount": Decimal("100.20"), "category": "material"}
    transaction = Transaction(**data)

    assert isinstance(transaction.transaction_date, date )

def test_amount_is_instance():
    data = {"transaction_id": 1, "description": "HOME_DEPOT", "transaction_date":  date(2026, 3, 3), "amount": Decimal("100.20"), "category": "material"}
    transaction = Transaction(**data)

    assert isinstance(transaction.amount, Decimal)