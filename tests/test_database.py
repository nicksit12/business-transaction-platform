from app.db.delete_statements import delete_statements, delete_specified_statement
from app.db.models import Statement, Transaction

from app.services.csv_reader import CSVReader

from app.services.merchant_classifier import MerchantClassifier
from pathlib import Path

from sqlalchemy import select, func



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

def test_delete_specified_statement(session):

    path = Path(__file__).parent / "data_test" / "chase_account_statement_mock.csv"
    statement = Statement(
        original_filename = path.name,
        file_hash = "test-hash"
    )
    transactions = CSVReader().read_path(path, statement)
    MerchantClassifier(session).classify(transactions)

    path2 = Path(__file__).parent / "data_test" / "chase_transactions_custom_headers.csv"
    statement2 = Statement(
        original_filename = path2.name,
        file_hash = "test-hash2"
        )
    transactions2 = CSVReader().read_path(path2, statement2)

    assert transactions2 

    MerchantClassifier(session).classify(transactions2)
    

    session.add(statement)
    session.flush()
    session.add(statement2)
    session.flush()

    statement_id = statement.id

    statement2_id = statement2.id

    
    length_of_transactions2 = session.scalar(select(func.count(Transaction.id)).where(Transaction.statement_id == statement2_id))
    length_of_transactions1 = session.scalar(select(func.count(Transaction.id)).where(Transaction.statement_id == statement_id))

    assert (length_of_transactions1 > 0)
    assert (length_of_transactions2 > 0)

    delete_specified_statement(session, statement_id)

    length_of_transactions1 = session.scalar(select(func.count(Transaction.id)).where(Transaction.statement_id == statement_id))
    length_of_transactions2 = session.scalar(select(func.count(Transaction.id)).where(Transaction.statement_id == statement2_id))

    assert (length_of_transactions1 == 0)
    assert (length_of_transactions2 > 0)

    




                           