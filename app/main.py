from collections import defaultdict
from decimal import Decimal
from io import StringIO

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.models.transaction import Transaction
from app.services.csv_reader import CSVImportError, read_csv, transactions_from_records
from app.services.merchantClassifier import categorize_transactions


app = FastAPI(
    title="Business Transaction Platform",
    description="Import and automatically categorize transaction CSV files.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Business Transaction Platform", "version": "1.0.0"}


def _serialize(transaction: Transaction) -> dict:
    return {
        "transaction_id": transaction.transaction_id,
        "transaction_date": transaction.transaction_date.isoformat(),
        "description": transaction.description,
        "amount": str(transaction.amount),
        "merchant": transaction.merchant,
        "category": transaction.category,
        "confidence": transaction.confidence,
    }


def _summarize(transactions: list[Transaction]) -> dict:
    category_totals: dict[str, Decimal] = defaultdict(Decimal)
    for transaction in transactions:
        category_totals[transaction.category] += transaction.amount

    income = sum((item.amount for item in transactions if item.amount > 0), Decimal())
    expenses = -sum((item.amount for item in transactions if item.amount < 0), Decimal())
    return {
        "transaction_count": len(transactions),
        "income": str(income),
        "expenses": str(expenses),
        "net": str(income - expenses),
        "category_totals": {
            category: str(amount) for category, amount in sorted(category_totals.items())
        },
    }


@app.post("/transactions/import")
async def import_transaction_csv(file: UploadFile = File(...)):
    if file.content_type not in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
        raise HTTPException(status_code=415, detail="Upload a CSV file.")

    try:
        content = (await file.read()).decode("utf-8-sig")
        transactions = transactions_from_records(read_csv(StringIO(content)))
        categorized = categorize_transactions(transactions)
    except (UnicodeDecodeError, CSVImportError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "summary": _summarize(categorized),
        "transactions": [_serialize(transaction) for transaction in categorized],
    }
