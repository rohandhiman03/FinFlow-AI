def test_generate_and_fetch_reports(client, complete_onboarding) -> None:
    user_id = "phase5-user"
    complete_onboarding(user_id)

    # Add some spending data before generating report.
    client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": user_id},
        json={"message": "coffee 6.50"},
    )
    client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": user_id},
        json={"message": "uber 18.20"},
    )

    generated = client.post(
        "/api/v1/reports/generate",
        headers={"X-User-Id": user_id},
    )
    assert generated.status_code == 200
    generated_body = generated.json()
    assert generated_body["overall_score"] >= 0
    assert generated_body["grade"] in {"A", "B", "C", "D", "F"}
    assert len(generated_body["dimensions"]) == 5
    assert len(generated_body["category_performance"]) > 0

    latest = client.get(
        "/api/v1/reports/latest",
        headers={"X-User-Id": user_id},
    )
    assert latest.status_code == 200
    latest_body = latest.json()
    assert latest_body["report_id"]
    assert latest_body["month"]

    history = client.get(
        "/api/v1/reports/history",
        headers={"X-User-Id": user_id},
    )
    assert history.status_code == 200
    history_body = history.json()
    assert len(history_body) >= 1


def test_generate_report_requires_budget(client) -> None:
    response = client.post(
        "/api/v1/reports/generate",
        headers={"X-User-Id": "phase5-no-budget"},
    )
    assert response.status_code == 400
    assert "Complete onboarding first" in response.json()["detail"]
