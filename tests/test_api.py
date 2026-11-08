import csv
from io import StringIO

from sqlalchemy import select

from app.db.models import Merchant


def test_statement_upload_classifies_and_persists(client):
    statement = (
        "description,transaction_date,amount\n"
        "STARBUCKS STORE 12,2026-08-01,-5.25\n"
        "LOCAL MYSTERY SHOP 991,2026-08-02,-10.00\n"
    )
    response = client.post(
        "/statements/upload",
        files={"file": ("statement.csv", statement, "text/csv")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["transaction_count"] == 2
    assert body["classified_count"] == 1
    assert body["unclassified_count"] == 1


def test_output_contains_only_unclassified_and_can_be_reuploaded(client):
    statement = (
        "description,transaction_date,amount\n"
        "STARBUCKS,2026-08-01,-5.25\n"
        "LOCAL MYSTERY SHOP,2026-08-02,-10.00\n"
    )
    upload = client.post(
        "/statements/upload",
        files={"file": ("statement.csv", statement, "text/csv")},
    )
    statement_id = upload.json()["statement_id"]

    output = client.get(f"/statements/{statement_id}/output")
    rows = list(csv.DictReader(StringIO(output.text)))
    assert output.status_code == 200
    assert len(rows) == 1
    assert rows[0]["description"] == "LOCAL MYSTERY SHOP"

    rows[0]["merchant"] = "Local Mystery Shop"
    rows[0]["category"] = "Office"
    correction = StringIO()
    writer = csv.DictWriter(correction, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    response = client.post(
        f"/statements/{statement_id}/reclassify",
        files={"file": ("corrections.csv", correction.getvalue(), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["updated_count"] == 1
    assert list(
        csv.DictReader(
            StringIO(client.get(f"/statements/{statement_id}/output").text)
        )
    ) == []


def test_upload_rejects_bad_headers(client):
    response = client.post(
        "/statements/upload",
        files={"file": ("statement.csv", "foo,bar\n1,2\n", "text/csv")},
    )
    assert response.status_code == 400


def test_get_merchant_transactions_returns_all_associated_transactions(
    client, session
):
    statement = (
        "description,transaction_date,amount\n"
        "STARBUCKS STORE 12,2026-08-02,-5.25\n"
        "STARBUCKS,2026-08-01,-4.75\n"
        "WHOLE FOODS,2026-08-03,-64.12\n"
    )
    upload = client.post(
        "/statements/upload",
        files={"file": ("statement.csv", statement, "text/csv")},
    )
    assert upload.status_code == 201

    merchant = session.scalar(
        select(Merchant).where(Merchant.canonical_name == "Starbucks")
    )
    response = client.get("/merchants/starbucks/transactions")

    assert response.status_code == 200
    body = response.json()
    assert body["merchant"] == {"id": merchant.id, "name": "Starbucks"}
    assert body["transaction_count"] == 2
    assert [row["description"] for row in body["transactions"]] == [
        "STARBUCKS",
        "STARBUCKS STORE 12",
    ]
    assert body["transactions"][0]["amount"] == -4.75


def test_get_merchant_transactions_returns_empty_list(client, session):
    merchant = session.scalar(
        select(Merchant).where(Merchant.canonical_name == "Amazon")
    )

    response = client.get(f"/merchants/{merchant.canonical_name}/transactions")

    assert response.status_code == 200
    assert response.json()["transaction_count"] == 0
    assert response.json()["transactions"] == []


def test_get_merchant_transactions_rejects_blank_name(client):
    response = client.get("/merchants/%20/transactions")

    assert response.status_code == 400
    assert response.json() == {"detail": "Merchant name is required."}


def test_get_merchant_transactions_rejects_oversized_name(client):
    response = client.get(f"/merchants/{'a' * 201}/transactions")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Merchant name must be 200 characters or fewer."
    }


def test_get_merchant_transactions_returns_not_found(client):
    response = client.get("/merchants/Unknown%20Merchant/transactions")

    assert response.status_code == 404
    assert response.json() == {"detail": "Merchant not found."}
