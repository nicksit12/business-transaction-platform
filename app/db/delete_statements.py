
from app.db.models import Statement, Transaction
from sqlalchemy import delete



def delete_statements(session):
    session.execute(delete(Transaction))    
    session.execute(delete(Statement))

def delete_specified_statement(session, spec_statement_id: int):

    statement = session.get(Statement, spec_statement_id)

    if statement is None:
        print("This statement dont exist")

    else:
    
        session.execute(delete(Transaction).where(Transaction.statement_id == spec_statement_id))
        session.execute(delete(Statement).where(Statement.id == spec_statement_id))
        print("Statement and transactions are deleted")
    



if __name__ == "__main__":
    delete_statements()
    print("Deleted session transactions from")

    
