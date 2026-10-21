from datetime import date
from decimal import Decimal

from app.schemas.transaction import Transaction
from app.services.merchantClassifier import (
    categorize_transactions,
    classify_transaction,
    normalize_description,
)


def transaction(description: str) -> Transaction:
    return Transaction(1, description, date(2026, 8, 1), Decimal("-10.00"))


def test_normalizes_description():
    assert normalize_description("  WHOLE   FOODS #123 ") == "whole foods 123"


def test_classifies_known_merchant():
    result = classify_transaction(transaction("WHOLE FOODS MARKET #104"))
    assert result.merchant == "Whole Foods"
    assert result.category == "Groceries & Supermarkets"
    assert result.confidence == 100.0


def test_unknown_merchant_is_preserved_for_manual_review():
    result = classify_transaction(transaction("LOCAL MYSTERY SHOP 991"))
    assert result.description == "LOCAL MYSTERY SHOP 991"
    assert result.merchant is None
    assert result.category == "Unclassified"


def test_categorizes_a_batch():
    results = categorize_transactions([transaction("UBER RIDES"), transaction("STARBUCKS")])
    assert [item.merchant for item in results] == ["Uber", "Starbucks"]
