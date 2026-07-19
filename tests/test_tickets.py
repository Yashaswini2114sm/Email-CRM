"""Tests for ticket endpoints."""
import pytest


@pytest.fixture()
def auth_headers(client):
    """Helper: register a user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "agent@example.com",
            "password": "password123",
            "full_name": "Test Agent",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "agent@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_ticket(client, auth_headers):
    """Should create a ticket with an initial message."""
    response = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "Need help with billing",
            "customer_email": "customer@example.com",
            "content": "I was charged twice for my subscription.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Need help with billing"
    assert data["status"] == "open"
    assert data["customer_email"] == "customer@example.com"


def test_list_tickets(client, auth_headers):
    """Should return a paginated list of tickets."""
    # Create 2 tickets
    for i in range(2):
        client.post(
            "/api/v1/tickets/",
            json={
                "subject": f"Ticket {i}",
                "customer_email": f"customer{i}@example.com",
                "content": f"Issue {i}",
            },
            headers=auth_headers,
        )

    response = client.get("/api/v1/tickets/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["tickets"]) == 2


def test_get_ticket_by_id(client, auth_headers):
    """Should fetch a single ticket by its UUID."""
    create = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "Specific ticket",
            "customer_email": "c@example.com",
            "content": "Details here",
        },
        headers=auth_headers,
    )
    ticket_id = create.json()["id"]

    response = client.get(
        f"/api/v1/tickets/{ticket_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["subject"] == "Specific ticket"


def test_update_ticket(client, auth_headers):
    """Should update ticket status and priority."""
    create = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "Updatable ticket",
            "customer_email": "u@example.com",
            "content": "Will be updated",
        },
        headers=auth_headers,
    )
    ticket_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}",
        json={"status": "in_progress", "priority": "high"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["priority"] == "high"


def test_ticket_messages(client, auth_headers):
    """Should create and retrieve messages on a ticket."""
    # Create ticket (which creates the first message)
    create = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "Message test",
            "customer_email": "msg@example.com",
            "content": "First message from customer",
        },
        headers=auth_headers,
    )
    ticket_id = create.json()["id"]

    # Send an agent reply
    client.post(
        f"/api/v1/tickets/{ticket_id}/messages",
        json={"content": "Agent reply here", "sender_type": "agent"},
        headers=auth_headers,
    )

    # Get all messages
    response = client.get(
        f"/api/v1/tickets/{ticket_id}/messages",
        headers=auth_headers,
    )
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["sender_type"] == "customer"
    assert messages[1]["sender_type"] == "agent"


def test_ticket_not_found(client, auth_headers):
    """Should return 404 for a non-existent ticket."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/tickets/{fake_id}", headers=auth_headers
    )
    assert response.status_code == 404
