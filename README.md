# Business Transaction Platform

This FastAPI service imports bank statement CSV files, stores statements and
transactions in SQLite, normalizes transaction descriptions, and classifies
known merchants. Transactions that cannot be classified can be downloaded,
edited, and uploaded again as corrections.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Statement formats

The standard format requires these columns (additional columns are ignored):

```csv
description,transaction_date,amount
WHOLE FOODS MARKET,2026-08-06,-64.12
```

Chase exports containing `Posting Date`, `Description`, and `Amount` are also
supported. Dates may be `YYYY-MM-DD` or `MM/DD/YYYY`. Amounts may be plain
decimals, currency values, or accounting negatives such as `($12.34)`.

## API workflow

Upload a statement:

```bash
curl -F "file=@statement.csv;type=text/csv" \
  http://127.0.0.1:8000/statements/upload
```

The response includes the statement ID and links for the next two operations.
Download only its unclassified transactions:

```bash
curl -o unclassified.csv \
  http://127.0.0.1:8000/statements/1/output
```

Fill in the `merchant` and `category` columns in that file, then upload it. Rows
are matched by the database `transaction_id`, and only those rows are updated:

```bash
curl -F "file=@unclassified.csv;type=text/csv" \
  http://127.0.0.1:8000/statements/1/reclassify
```

Manual corrections also create the merchant alias when needed, so later
statements can classify that merchant automatically.
