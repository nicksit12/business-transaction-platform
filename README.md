# Business Transaction Platform

Release 1 is a small FastAPI service and Python pipeline that imports transaction
CSV files, identifies known merchants, assigns spending categories, and preserves
uncertain transactions for manual review.

## Release 1 features

- Imports the app's standard CSV format and Chase activity exports.
- Normalizes merchant descriptions and performs exact-then-fuzzy matching.
- Keeps merchant/category configuration in `app/data/merchants.json`.
- Marks low-confidence matches as `Unclassified` without dropping them.
- Categorizes a full CSV and exports enriched results to another CSV.
- Provides an HTTP upload endpoint with totals and categorized transactions.

## Setup

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the tests:

```bash
pytest -q
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## CSV formats

The standard format is:

```csv
transaction_id,description,transaction_date,amount,category
TXN-1,WHOLE FOODS MARKET,2026-08-06,-64.12,
```

Dates may use `YYYY-MM-DD` or `MM/DD/YYYY`. Amounts may be plain decimals,
currency values, or accounting-style negatives such as `($12.34)`. A Chase CSV
must include at least `Posting Date`, `Description`, and `Amount`.

Upload a file:

```bash
curl -F "file=@transactions.csv;type=text/csv" \
  http://127.0.0.1:8000/transactions/import
```

## Use the pipeline from Python

```python
from app.services.csv_reader import import_transactions
from app.services.csv_writer import export_transactions
from app.services.merchantClassifier import categorize_transactions

transactions = import_transactions("transactions.csv")
categorized = categorize_transactions(transactions)
export_transactions(categorized, "categorized.csv")
```

Exported files contain transaction ID, date, original description, amount,
canonical merchant, category, and confidence score. Edit
`app/data/merchants.json` to add or reorganize supported merchants.
