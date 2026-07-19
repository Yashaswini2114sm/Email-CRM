"""Tests for authentication endpoints."""


def test_health_check(client):
    """The health endpoint should always return ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_user(client):
    """Should create a new user and return their profile."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    # Password should never be returned
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    """Should reject registration with an existing email."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "User One",
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Try to register again with the same email
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400


def test_login_success(client):
    """Should return a JWT token for valid credentials."""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "mypassword",
            "full_name": "Login User",
        },
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "mypassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Should reject login with incorrect password."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "correctpassword",
            "full_name": "Wrong Pass User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_me_authenticated(client):
    """Should return the current user's profile when authenticated."""
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123",
            "full_name": "Me User",
        },
    )

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Get profile
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_get_me_unauthenticated(client):
    """Should return 401 without a token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
