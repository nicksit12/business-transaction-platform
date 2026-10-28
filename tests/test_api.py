import csv
from io import StringIO


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
