def test_goals_create_list_and_contribute(client, complete_onboarding) -> None:
    user_id = "phase7-user"
    complete_onboarding(user_id)

    created = client.post(
        "/api/v1/goals",
        headers={"X-User-Id": user_id},
        json={"name": "Emergency Fund", "target_amount": 9000, "target_date": "2026-12-31"},
    )
    assert created.status_code == 200
    goal_id = created.json()["goal_id"]

    listed = client.get("/api/v1/goals", headers={"X-User-Id": user_id})
    assert listed.status_code == 200
    goals = listed.json()
    assert len(goals) >= 1

    contribute = client.post(
        f"/api/v1/goals/{goal_id}/contribute",
        headers={"X-User-Id": user_id},
        json={"amount": 500},
    )
    assert contribute.status_code == 200
    body = contribute.json()
    assert body["current_amount"] == 500
    assert body["progress_pct"] > 0


def test_digest_settings_and_weekly_digest(client, complete_onboarding) -> None:
    user_id = "phase7-digest"
    complete_onboarding(user_id)

    settings = client.get("/api/v1/digest/settings", headers={"X-User-Id": user_id})
    assert settings.status_code == 200

    updated = client.put(
        "/api/v1/digest/settings",
        headers={"X-User-Id": user_id},
        json={"frequency": "weekly", "day": "Sunday", "time": "08:30"},
    )
    assert updated.status_code == 200
    assert updated.json()["time"] == "08:30"

    digest = client.get("/api/v1/digest/weekly", headers={"X-User-Id": user_id})
    assert digest.status_code == 200
    digest_body = digest.json()
    assert digest_body["digest_text"]
    assert digest_body["weekly_spent"] >= 0
    assert isinstance(digest_body["upcoming_expenses"], list)


def test_digest_requires_budget(client) -> None:
    response = client.get("/api/v1/digest/weekly", headers={"X-User-Id": "phase7-no-budget"})
    assert response.status_code == 400
    assert "Complete onboarding first" in response.json()["detail"]
