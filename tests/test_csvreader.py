import pytest
import pytest
from decimal import Decimal
from datetime import date
from app.models.transaction import Transaction
from app.services.csv_reader import *


def test_csvreader():
    filepath = "/Users/nicksit/DataAnalytics/business-transaction-platform/tests/data/chase_transactions_custom_headers.csv"
    transactions = import_transactions(filepath) 
    assert isinstance(transactions, list)
    assert all(isinstance(t, Transaction) for t in transactions)



