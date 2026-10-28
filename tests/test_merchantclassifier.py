from datetime import date
from decimal import Decimal

from app.db.models import Statement, Transaction
from app.services.merchant_classifier import MerchantClassifier, normalize_description


def make_transaction(description):
    statement = Statement(original_filename="test.csv", file_hash=description)
    return Transaction(
        statement=statement,
        source_row_number=1,
        transaction_date=date(2026, 8, 1),
        description=description,
        normalized_description="",
        amount=Decimal("-10.00"),
        classification_status="unclassified",
    )


def test_normalizes_description():
    assert normalize_description("  WHOLE   FOODS #123 ") == "whole foods 123"


def test_classifier_updates_database_transaction(session):
    transaction = make_transaction("WHOLE FOODS MARKET #104")

    MerchantClassifier(session).classify([transaction])

    assert transaction.normalized_description == "whole foods market 104"
    assert transaction.merchant.canonical_name == "Whole Foods"
    assert transaction.category.name == "Groceries"
    assert transaction.classification_status == "classified"


def test_unknown_transaction_stays_unclassified(session):
    transaction = make_transaction("LOCAL MYSTERY SHOP 991")

    MerchantClassifier(session).classify([transaction])

    assert transaction.merchant is None
    assert transaction.category is None
    assert transaction.classification_status == "unclassified"
