def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Ecommerce API is running"}


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Casey", "email": "casey@example.com", "password": "test-password"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "casey@example.com"
    assert response.json()["role"] == "customer"
    assert "password" not in response.json()


def test_register_rejects_duplicate_email(client):
    payload = {"name": "Casey", "email": "casey@example.com", "password": "test-password"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_and_get_current_user(client):
    client.post(
        "/auth/register",
        json={"name": "Casey", "email": "casey@example.com", "password": "test-password"},
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "casey@example.com", "password": "test-password"},
    )
    token = login_response.json()["access_token"]
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "casey@example.com"


def test_login_rejects_invalid_password(client):
    client.post(
        "/auth/register",
        json={"name": "Casey", "email": "casey@example.com", "password": "test-password"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "casey@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
