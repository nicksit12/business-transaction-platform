from sqlalchemy import func, select

from app.db.models import (
    Category,
    Merchant,
    MerchantAlias,
    Transaction,
    Statement
)
from app.db.session import SessionLocal


def check_database() -> None:
    with SessionLocal() as session:
        category_count = session.scalar(
            select(func.count()).select_from(Category)
        )

        merchant_count = session.scalar(
            select(func.count()).select_from(Merchant)
        )

        alias_count = session.scalar(
            select(func.count()).select_from(
                MerchantAlias
            )
        )

        transaction_count = session.scalar(select(func.count()).select_from(Transaction))
        statement_count = session.scalar(select(func.count()).select_from(Statement))

        print("Categories:", category_count)
        print("Merchants:", merchant_count)
        print("Aliases:", alias_count)
        print("transactions:", transaction_count)
        print("statements:", statement_count)



if __name__ == "__main__":
    check_database()