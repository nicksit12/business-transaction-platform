import json
from pathlib import Path

from sqlalchemy import select
from csv import DictReader

from app.db.models import (
    Category, 
    Merchant, 
    MerchantAlias
)

from app.db.session import SessionLocal
from app.services.merchantClassifier import load_merchants, normalize_description

FILE_MERCHANTS = "app/data/merchants.json"

#create a session 

def seed_merchants() -> None:
    merchant_data = load_merchants()

    with SessionLocal.begin() as session:
        for category_name, merchant_names in merchant_data.items():
            category = get_or_create_category(
                session,
                category_name,
            )

            for merchant_name in merchant_names:
                merchant_name = merchant_name.strip()

                if not merchant_name:
                    continue

                merchant = session.scalar(
                    select(Merchant).where(
                        Merchant.canonical_name
                        == merchant_name
                    )
                )

                if merchant is None:
                    merchant = Merchant(
                        canonical_name=merchant_name,
                        default_category=category,
                    )

                    session.add(merchant)
                    session.flush()

                normalized_alias = normalize_description(
                    merchant_name
                )

                alias = session.scalar(
                    select(MerchantAlias).where(
                        MerchantAlias.normalized_alias
                        == normalized_alias
                    )
                )

                if alias is None:
                    alias = MerchantAlias(
                        merchant=merchant,
                        normalized_alias=normalized_alias,
                    )

                    session.add(alias)
        
    
def get_or_create_category(
    session,
    category_name: str,
) -> Category:
    category = session.scalar(
        select(Category).where(
            Category.name == category_name
        )
    )

    if category is None:
        category = Category(
            name=category_name,
            category_type="expense",
        )

        session.add(category)
        session.flush()

    return category


if __name__ == "__main__":
    seed_merchants()
    print("Period")