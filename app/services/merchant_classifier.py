import re

from rapidfuzz import fuzz, process
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MerchantAlias, Transaction


DEFAULT_THRESHOLD = 90.0


def normalize_description(description: str) -> str:
    normalized = re.sub(r"[^a-z0-9&+]+", " ", description.lower())
    return " ".join(normalized.split())


class MerchantClassifier:
    def __init__(self, session: Session, threshold: float = DEFAULT_THRESHOLD):
        self.session = session
        self.threshold = threshold

    def classify(self, transactions: list[Transaction]) -> list[Transaction]:
        aliases = self.session.scalars(select(MerchantAlias)).all()
        aliases_by_name = {alias.normalized_alias: alias for alias in aliases}

        for transaction in transactions:
            self.session.add(transaction)
            transaction.normalized_description = normalize_description(
                transaction.description
            )
            transaction.merchant = None
            transaction.category = None
            transaction.classification_status = "unclassified"
            transaction.classification_confidence = 0.0

            match = self._find_match(
                transaction.normalized_description, aliases_by_name
            )
            if match is None:
                continue

            alias, confidence = match
            transaction.merchant = alias.merchant
            transaction.category = alias.merchant.default_category
            transaction.classification_status = "classified"
            transaction.classification_confidence = round(confidence, 1)

        return transactions

    def _find_match(self, description, aliases_by_name):
        if not aliases_by_name:
            return None

        padded_description = " " + description + " "
        exact_matches = [
            name
            for name in aliases_by_name
            if " " + name + " " in padded_description
        ]
        if exact_matches:
            name = max(exact_matches, key=len)
            return aliases_by_name[name], 100.0

        match = process.extractOne(
            description,
            aliases_by_name.keys(),
            scorer=fuzz.WRatio,
        )
        if match is None or match[1] < self.threshold:
            return None

        return aliases_by_name[match[0]], float(match[1])
