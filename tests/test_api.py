from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_reports_release_version():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_import_endpoint_categorizes_csv():
    csv_content = (
        "transaction_id,description,transaction_date,amount,category\n"
        "TXN-1,STARBUCKS STORE 12,2026-08-01,-5.25,\n"
    )
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["transaction_count"] == 1
    assert body["summary"]["expenses"] == "5.25"
    assert body["transactions"][0]["merchant"] == "Starbucks"


def test_import_endpoint_rejects_bad_headers():
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", "foo,bar\n1,2\n", "text/csv")},
    )
    assert response.status_code == 400
