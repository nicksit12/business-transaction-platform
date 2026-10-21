import pytest
from pathlib import Path

from app.schemas.transaction import Transaction
from app.services.csv_reader import import_transactions


def test_csvreader():
    filepath = Path(__file__).parent / "data_test" / "chase_transactions_custom_headers.csv"
    transactions = import_transactions(filepath) 
    assert isinstance(transactions, list)
    assert all(isinstance(t, Transaction) for t in transactions)


