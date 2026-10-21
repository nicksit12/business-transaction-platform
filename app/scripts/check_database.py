from sqlalchemy import func, select

from app.db.models import (
    Category,
    Merchant,
    MerchantAlias,
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

        print("Categories:", category_count)
        print("Merchants:", merchant_count)
        print("Aliases:", alias_count)


if __name__ == "__main__":
    check_database()