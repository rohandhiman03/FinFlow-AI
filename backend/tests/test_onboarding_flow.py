from app.db.models import Budget, BudgetCategory, Goal


def test_onboarding_start_returns_first_prompt(client) -> None:
    response = client.post(
        "/api/v1/onboarding/start",
        headers={"X-User-Id": "phase2-user"},
        json={"reset_existing": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "active"
    assert body["current_step"] == "income"
    assert body["provider"] in {"claude", "gemini", "grok"}
    assert len(body["messages"]) == 1
    assert body["messages"][0]["role"] == "assistant"


def test_onboarding_full_flow_creates_budget_and_goal(client, complete_onboarding) -> None:
    complete_onboarding("phase2-user")

    from app.db.database import SessionLocal

    with SessionLocal() as db:
        budgets = db.query(Budget).filter(Budget.user_id == "phase2-user").all()
        categories = db.query(BudgetCategory).all()
        goals = db.query(Goal).filter(Goal.user_id == "phase2-user").all()

    assert len(budgets) >= 1
    assert len(categories) >= 1
    assert len(goals) >= 1
