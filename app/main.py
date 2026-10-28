import csv
import hashlib
from io import StringIO

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.dependencies import get_session
from app.db.models import Category, Merchant, MerchantAlias, Statement, Transaction
from app.db.session import engine
from app.scripts.seed_merchants import seed_merchants
from app.services.csv_reader import CSVImportError, CSVReader
from app.services.csv_writer import CSVWriter
from app.services.merchant_classifier import MerchantClassifier, normalize_description


Base.metadata.create_all(bind=engine)
seed_merchants()

app = FastAPI(
    title="Business Transaction Platform",
    description="Upload, classify, review, and correct transaction statements.",
    version="2.0.0",
)


@app.get("/")
def root():
    return {"message": "Business Transaction Platform", "version": "2.0.0"}


def read_upload(content: bytes) -> StringIO:
    try:
        return StringIO(content.decode("utf-8-sig"))
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="The CSV must use UTF-8 encoding.") from error


@app.post("/statements/upload", status_code=201)
async def upload_statement(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    duplicate = session.scalar(
        select(Statement).where(Statement.file_hash == file_hash)
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"This statement was already uploaded as statement {duplicate.id}.",
        )

    statement = Statement(
        original_filename=file.filename or "statement.csv",
        file_hash=file_hash,
    )

    try:
        transactions = CSVReader().read(read_upload(content), statement)
        if not transactions:
            raise CSVImportError("The statement does not contain any transactions.")
        MerchantClassifier(session).classify(transactions)
        session.add(statement)
        session.commit()
    except CSVImportError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(error)) from error

    unclassified_count = sum(
        transaction.classification_status == "unclassified"
        for transaction in transactions
    )
    return {
        "statement_id": statement.id,
        "filename": statement.original_filename,
        "transaction_count": len(transactions),
        "classified_count": len(transactions) - unclassified_count,
        "unclassified_count": unclassified_count,
        "unclassified_output": f"/statements/{statement.id}/output",
        "reclassification_upload": f"/statements/{statement.id}/reclassify",
    }


@app.get("/statements/{statement_id}/output")
def output_unclassified_statement(
    statement_id: int,
    session: Session = Depends(get_session),
):
    statement = session.get(Statement, statement_id)
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found.")

    transactions = session.scalars(
        select(Transaction)
        .where(
            Transaction.statement_id == statement_id,
            Transaction.classification_status == "unclassified",
        )
        .order_by(Transaction.source_row_number)
    ).all()

    output = StringIO()
    CSVWriter().write(list(transactions), output)
    filename = f"statement-{statement_id}-unclassified.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/statements/{statement_id}/reclassify")
async def reclassify_transactions(
    statement_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    statement = session.get(Statement, statement_id)
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found.")

    reader = csv.DictReader(read_upload(await file.read()))
    required_headers = {"transaction_id", "merchant", "category"}
    if not reader.fieldnames or not required_headers.issubset(reader.fieldnames):
        raise HTTPException(
            status_code=400,
            detail="The correction CSV requires transaction_id, merchant, and category.",
        )

    updated_ids = []
    for row_number, row in enumerate(reader, start=2):
        try:
            transaction_id = int(row["transaction_id"])
        except (TypeError, ValueError):
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transaction_id on row {row_number}.",
            )

        merchant_name = (row["merchant"] or "").strip()
        category_name = (row["category"] or "").strip()
        if not merchant_name or not category_name:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Merchant and category are required on row {row_number}.",
            )

        transaction = session.scalar(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.statement_id == statement_id,
            )
        )
        if transaction is None:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Transaction {transaction_id} is not in statement {statement_id}.",
            )

        category = get_or_create_category(session, category_name)
        merchant = get_or_create_merchant(session, merchant_name, category)
        get_or_create_alias(session, merchant, merchant_name)

        transaction.merchant = merchant
        transaction.category = category
        transaction.classification_status = "manually_classified"
        transaction.classification_confidence = 100.0
        updated_ids.append(transaction.id)

    session.commit()
    return {
        "statement_id": statement_id,
        "updated_count": len(updated_ids),
        "updated_transaction_ids": updated_ids,
    }


def get_or_create_category(session: Session, name: str) -> Category:
    category = session.scalar(select(Category).where(Category.name == name))
    if category is None:
        category = Category(name=name, category_type="expense")
        session.add(category)
        session.flush()
    return category


def get_or_create_merchant(
    session: Session, name: str, category: Category
) -> Merchant:
    merchant = session.scalar(
        select(Merchant).where(Merchant.canonical_name == name)
    )
    if merchant is None:
        merchant = Merchant(canonical_name=name, default_category=category)
        session.add(merchant)
        session.flush()
    else:
        merchant.default_category = category
    return merchant


def get_or_create_alias(
    session: Session, merchant: Merchant, merchant_name: str
) -> MerchantAlias:
    normalized_alias = normalize_description(merchant_name)
    alias = session.scalar(
        select(MerchantAlias).where(
            MerchantAlias.normalized_alias == normalized_alias
        )
    )
    if alias is None:
        alias = MerchantAlias(
            merchant=merchant,
            normalized_alias=normalized_alias,
        )
        session.add(alias)
    return alias
