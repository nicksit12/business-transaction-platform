from pathlib import Path

from app.db.models import Statement, Transaction
from app.services.csv_reader import CSVReader


def test_csv_reader_creates_database_transactions():
    path = Path(__file__).parent / "data_test" / "chase_transactions_custom_headers.csv"
    statement = Statement(original_filename=path.name, file_hash="test-hash")

    transactions = CSVReader().read_path(path, statement)

    assert transactions
    assert all(isinstance(transaction, Transaction) for transaction in transactions)
    assert transactions[0].statement is statement
    assert transactions[0].source_row_number == 1
