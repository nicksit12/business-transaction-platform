import csv
from pathlib import Path

from app.services.csv_reader import import_transactions
from app.services.csv_writer import export_transactions
from app.services.merchantClassifier import categorize_transactions


DATA = Path(__file__).parent / "data_test"


def test_csv_to_categorized_export(tmp_path):
    transactions = import_transactions(DATA / "chase_account_statement_mock.csv")
    categorized = categorize_transactions(transactions)
    output = export_transactions(categorized, tmp_path / "categorized.csv")

    with output.open(newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 20
    assert rows[14]["description"] == "AMAZON.COM"
    assert rows[14]["merchant"] == "Amazon"
    assert rows[14]["category"] == "Retail & E-Commerce"
    assert rows[16]["merchant"] == "Uber"
    assert rows[17]["merchant"] == "Whole Foods"
    assert rows[18]["merchant"] == "Starbucks"
