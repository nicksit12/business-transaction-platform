import csv
from io import StringIO
from pathlib import Path

from app.db.models import Statement
from app.services.csv_reader import CSVReader
from app.services.csv_writer import CSVWriter
from app.services.merchant_classifier import MerchantClassifier


def test_csv_to_database_to_output(session):
    path = Path(__file__).parent / "data_test" / "chase_account_statement_mock.csv"
    statement = Statement(original_filename=path.name, file_hash="pipeline-test")
    transactions = CSVReader().read_path(path, statement)

    MerchantClassifier(session).classify(transactions)
    session.add(statement)
    session.flush()

    output = StringIO()
    CSVWriter().write(transactions, output)
    rows = list(csv.DictReader(StringIO(output.getvalue())))

    assert len(rows) == 20
    assert rows[14]["merchant"] == "Amazon"
    assert rows[16]["merchant"] == "Uber"
    assert rows[17]["merchant"] == "Whole Foods"
    assert rows[18]["merchant"] == "Starbucks"
