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


def test_onboarding_full_flow_creates_budget_and_goal(client) -> None:
    start = client.post(
        "/api/v1/onboarding/start",
        headers={"X-User-Id": "phase2-user"},
        json={"reset_existing": True},
    )
    session_id = start.json()["session_id"]

    sequence = [
        "Salary 5000 monthly",
        "Rent 1800, phone 80, internet 60",
        "Groceries 600, dining 300, transport 200",
        "Emergency fund 10000",
        "confirm",
    ]

    last = None
    for msg in sequence:
        last = client.post(
            "/api/v1/onboarding/message",
            headers={"X-User-Id": "phase2-user"},
            json={"session_id": session_id, "message": msg},
        )
        assert last.status_code == 200

    assert last is not None
    body = last.json()
    assert body["status"] == "completed"
    assert body["current_step"] == "completed"
    assert body["budget_proposal"] is not None

    # Validate persistence by checking onboarding generated records exist.
    from app.db.database import SessionLocal

    with SessionLocal() as db:
        budgets = db.query(Budget).filter(Budget.user_id == "phase2-user").all()
        categories = db.query(BudgetCategory).all()
        goals = db.query(Goal).filter(Goal.user_id == "phase2-user").all()

    assert len(budgets) >= 1
    assert len(categories) >= 1
    assert len(goals) >= 1
