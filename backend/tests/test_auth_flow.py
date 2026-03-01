def test_register_login_and_me_with_dev_identity(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "user1@example.com", "password": "test-pass-123"},
    )
    assert register.status_code == 200
    user_id = register.json()["user_id"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "test-pass-123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"X-User-Id": user_id},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "user1@example.com"


def test_register_conflict(client) -> None:
    payload = {"email": "dup@example.com", "password": "abc123456"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
