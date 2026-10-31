from app.db.delete_statements import delete_statements
from app.db.models import Statement, Transaction

from app.services.csv_reader import CSVReader

from app.services.merchant_classifier import MerchantClassifier
from pathlib import Path



def test_delete_statements(session):

    path = Path(__file__).parent / "data_test" / "chase_account_statement_mock.csv"
    statement = Statement(original_filename=path.name,file_hash="delete-hash-test")

    transactions = CSVReader().read_path(path, statement)

    amount_of_transactions = len(transactions)

    assert transactions
    MerchantClassifier(session).classify(transactions)
    session.add(statement)
    session.flush()

    added_transactions = session.query(Transaction).all()

    assert (len(added_transactions) == amount_of_transactions)

    delete_statements(session)

    session.flush()

    added_transactions = session.query(Transaction).all()

    assert (added_transactions == [])



                           