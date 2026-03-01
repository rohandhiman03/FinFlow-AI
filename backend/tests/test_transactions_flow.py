def test_log_expense_and_get_budget_summary(client, complete_onboarding) -> None:
    user_id = "phase3-user"
    complete_onboarding(user_id)

    log_response = client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": user_id},
        json={"message": "grabbed coffee $4.75"},
    )

    assert log_response.status_code == 200
    body = log_response.json()
    assert body["transaction"]["amount"] == 4.75
    assert body["transaction"]["category_name"] in {"Dining", "Lifestyle", "Groceries", "Transport", "Utilities", "Housing", "Savings"}
    assert "Added $4.75" in body["confirmation"]

    summary_response = client.get(
        "/api/v1/transactions/budget-summary",
        headers={"X-User-Id": user_id},
    )

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_spent"] >= 4.75
    assert summary["total_planned"] > 0
    assert len(summary["categories"]) > 0


def test_log_expense_requires_budget(client) -> None:
    response = client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": "no-budget-user"},
        json={"message": "coffee $5"},
    )
    assert response.status_code == 400
    assert "Complete onboarding first" in response.json()["detail"]
