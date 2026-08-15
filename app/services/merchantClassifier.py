import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from rapidfuzz import fuzz, process

from app.models.transaction import Transaction


DEFAULT_THRESHOLD = 90.0
MAX_THRESHOLD = DEFAULT_THRESHOLD  # Backwards-compatible name.
MERCHANT_DATA_PATH = Path(__file__).parents[1] / "data" / "merchants.json"


@dataclass(frozen=True)
class MerchantMatch:
    merchant: str | None
    category: str
    confidence: float


def normalize_description(description: str) -> str:
    """Lowercase text and collapse punctuation/whitespace for matching."""
    normalized = re.sub(r"[^a-z0-9&+]+", " ", description.lower())
    return " ".join(normalized.split())


def load_merchants(path: str | Path = MERCHANT_DATA_PATH) -> dict[str, list[str]]:
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not all(isinstance(value, list) for value in data.values()):
        raise ValueError("Merchant data must map category names to merchant lists.")
    return data


def flatten_merchants(
    merchant_categories: Mapping[str, Sequence[str]],
) -> dict[str, tuple[str, str]]:
    flattened = {}
    for category, merchant_names in merchant_categories.items():
        for merchant in merchant_names:
            flattened[normalize_description(merchant)] = (merchant, category)
    return flattened


MERCHANTS = load_merchants()
merchants = MERCHANTS  # Backwards-compatible name.
FLATTENED_MERCHANTS = flatten_merchants(MERCHANTS)


def classify_merchant(
    flattened_merchants: Mapping[str, tuple[str, str] | str],
    transaction: Transaction,
) -> tuple[str, float, int] | None:
    """Return RapidFuzz's match tuple for compatibility with the prototype API."""
    description = normalize_description(transaction.description)
    if not flattened_merchants:
        return None
    return process.extractOne(description, flattened_merchants.keys(), scorer=fuzz.WRatio)


def match_merchant(
    description: str,
    flattened_merchants: Mapping[str, tuple[str, str]] = FLATTENED_MERCHANTS,
    threshold: float = DEFAULT_THRESHOLD,
) -> MerchantMatch:
    normalized = normalize_description(description)

    # Prefer the longest literal merchant contained in a bank description.
    padded_description = f" {normalized} "
    exact_candidates = [
        name for name in flattened_merchants if f" {name} " in padded_description
    ]
    if exact_candidates:
        key = max(exact_candidates, key=len)
        merchant, category = flattened_merchants[key]
        return MerchantMatch(merchant, category, 100.0)

    fuzzy_match = process.extractOne(normalized, flattened_merchants.keys(), scorer=fuzz.WRatio)
    if fuzzy_match is None or fuzzy_match[1] < threshold:
        return MerchantMatch(None, "Unclassified", float(fuzzy_match[1]) if fuzzy_match else 0.0)

    key, score, _ = fuzzy_match
    merchant, category = flattened_merchants[key]
    return MerchantMatch(merchant, category, float(score))


def classify_transaction(
    transaction: Transaction, threshold: float = DEFAULT_THRESHOLD
) -> Transaction:
    match = match_merchant(transaction.description, threshold=threshold)
    transaction.merchant = match.merchant
    transaction.category = match.category
    transaction.confidence = round(match.confidence, 1)
    return transaction


def categorize_transactions(
    transactions: Iterable[Transaction], threshold: float = DEFAULT_THRESHOLD
) -> list[Transaction]:
    return [classify_transaction(transaction, threshold) for transaction in transactions]
