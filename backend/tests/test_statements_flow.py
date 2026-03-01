from datetime import datetime, timezone


def test_statement_upload_and_reconciliation(client, complete_onboarding) -> None:
    user_id = "phase4-user"
    complete_onboarding(user_id)

    # Existing logged transaction to be auto-matched.
    log_response = client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": user_id},
        json={"message": "grabbed coffee $4.75"},
    )
    assert log_response.status_code == 200

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    csv_content = (
        "date,description,amount\n"
        f"{today},Coffee Shop,4.75\n"
        f"{today},Rogers Bill,95.00\n"
    )

    upload = client.post(
        "/api/v1/statements/upload",
        headers={"X-User-Id": user_id},
        data={"account_name": "TD Visa"},
        files={"file": ("statement.csv", csv_content.encode("utf-8"), "text/csv")},
    )

    assert upload.status_code == 200
    upload_body = upload.json()
    assert upload_body["transactions_found"] == 2
    statement_id = upload_body["statement_id"]

    reconciliation = client.get(
        f"/api/v1/statements/{statement_id}/reconciliation",
        headers={"X-User-Id": user_id},
    )

    assert reconciliation.status_code == 200
    recon_body = reconciliation.json()
    assert recon_body["statement_id"] == statement_id
    assert len(recon_body["matched"]) >= 1
    assert len(recon_body["gaps"]) >= 1

    gap_entry_id = recon_body["gaps"][0]["entry_id"]
    confirm = client.post(
        f"/api/v1/statements/{statement_id}/gaps/{gap_entry_id}/confirm",
        headers={"X-User-Id": user_id},
        json={"category_name": "Utilities"},
    )

    assert confirm.status_code == 200
    confirm_body = confirm.json()
    assert confirm_body["status"] == "matched"
    assert "Logged" in confirm_body["confirmation"]


def test_statement_upload_requires_budget(client) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    csv_content = f"date,description,amount\n{today},Coffee,4.75\n"

    upload = client.post(
        "/api/v1/statements/upload",
        headers={"X-User-Id": "phase4-no-budget"},
        data={"account_name": "Any"},
        files={"file": ("statement.csv", csv_content.encode("utf-8"), "text/csv")},
    )

    assert upload.status_code == 400
    assert "Complete onboarding first" in upload.json()["detail"]
