def test_advisory_ask_and_apply_suggestion(client, complete_onboarding) -> None:
    user_id = "phase6-user"
    complete_onboarding(user_id)

    # Force low remaining budget by adding high expenses.
    client.post(
        "/api/v1/transactions/log",
        headers={"X-User-Id": user_id},
        json={"message": "big shopping 4300"},
    )

    ask = client.post(
        "/api/v1/advisory/ask",
        headers={"X-User-Id": user_id},
        json={"message": "I want to buy a $800 laptop this month, can I swing it?"},
    )

    assert ask.status_code == 200
    ask_body = ask.json()
    assert ask_body["session_id"]
    assert isinstance(ask_body["reasoning"], list)
    assert len(ask_body["reasoning"]) >= 1

    # Suggestion may appear depending on remaining budget.
    if ask_body["suggestions"]:
        suggestion_id = ask_body["suggestions"][0]["suggestion_id"]
        apply_resp = client.post(
            "/api/v1/advisory/apply",
            headers={"X-User-Id": user_id},
            json={"suggestion_id": suggestion_id},
        )
        assert apply_resp.status_code == 200
        apply_body = apply_resp.json()
        assert apply_body["status"] == "applied"
        assert "Applied" in apply_body["confirmation"]


def test_advisory_requires_budget(client) -> None:
    response = client.post(
        "/api/v1/advisory/ask",
        headers={"X-User-Id": "phase6-no-budget"},
        json={"message": "Can I buy a 500 phone?"},
    )

    assert response.status_code == 400
    assert "Complete onboarding first" in response.json()["detail"]
