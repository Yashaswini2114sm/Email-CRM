"""Tests for AI endpoints."""
from unittest.mock import patch

import pytest


@pytest.fixture()
def auth_headers(client):
    """Helper: register a user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "ai_agent@example.com",
            "password": "password123",
            "full_name": "AI Test Agent",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ai_agent@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_ticket(client, auth_headers):
    """Helper: create a ticket and return its ID."""
    response = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "AI test ticket",
            "customer_email": "customer@example.com",
            "content": "I was charged twice for my subscription.",
        },
        headers=auth_headers,
    )
    return response.json()["id"]


def test_analyze_without_openai_key(client, auth_headers):
    """Should return unknown intent when OpenAI key is not configured."""
    with patch("src.services.ai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""

        response = client.post(
            "/api/v1/ai/analyze",
            json={"message": "I want a refund for my order"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "unknown"
        assert data["confidence"] == 0.0


def test_analyze_with_ticket_id(client, auth_headers, sample_ticket):
    """Should save the detected intent on the ticket."""
    with patch("src.services.ai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""

        response = client.post(
            "/api/v1/ai/analyze",
            json={
                "message": "I want a refund",
                "ticket_id": sample_ticket,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify the ticket was updated with the intent
        ticket = client.get(
            f"/api/v1/tickets/{sample_ticket}",
            headers=auth_headers,
        )
        assert ticket.status_code == 200
        assert ticket.json()["intent"] == "unknown"


def test_generate_reply_without_openai_key(
    client, auth_headers, sample_ticket
):
    """Should return a fallback reply when OpenAI is not configured."""
    with patch("src.services.ai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""

        response = client.post(
            "/api/v1/ai/generate-reply",
            json={"ticket_id": sample_ticket},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "message_id" in data
        # Should contain the fallback message
        assert "agent will respond" in data["reply"].lower()


def test_generate_reply_ticket_not_found(client, auth_headers):
    """Should return 404 for a non-existent ticket."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/ai/generate-reply",
        json={"ticket_id": fake_id},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_validate_documents_empty(client, auth_headers, sample_ticket):
    """Should report missing documents when none are uploaded."""
    response = client.post(
        "/api/v1/ai/validate-documents",
        json={
            "ticket_id": sample_ticket,
            "required_documents": ["id_proof", "address_proof"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["all_valid"] is False
    assert "id_proof" in data["missing_documents"]
    assert "address_proof" in data["missing_documents"]
    assert data["submitted_documents"] == []


def test_ai_endpoints_unauthenticated(client):
    """All AI endpoints should require authentication."""
    assert client.post(
        "/api/v1/ai/analyze", json={"message": "test"}
    ).status_code == 401

    assert client.post(
        "/api/v1/ai/generate-reply",
        json={"ticket_id": "00000000-0000-0000-0000-000000000000"},
    ).status_code == 401
