
from app.db.models import Statement, Transaction
from sqlalchemy import delete



def delete_statements(session):

    session.execute(delete(Transaction))    
    session.execute(delete(Statement))
    session.flush()


if __name__ == "__main__":
    delete_statements()
    print("Deleted session transactions from")

    
