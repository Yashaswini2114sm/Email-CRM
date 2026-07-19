"""Tests for email endpoints."""
from unittest.mock import patch

import pytest


@pytest.fixture()
def auth_headers(client):
    """Helper: register a user with admin role and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "password123",
            "full_name": "Admin User",
            "role": "admin",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def agent_headers(client):
    """Helper: register a regular agent and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "agent@example.com",
            "password": "password123",
            "full_name": "Agent User",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "agent@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_process_emails_no_credentials(client, auth_headers):
    """Should return empty results when email credentials are not configured."""
    with patch(
        "src.services.email_service.settings"
    ) as mock_settings:
        mock_settings.MAIL_USERNAME = ""
        mock_settings.MAIL_PASSWORD = ""

        response = client.post(
            "/api/v1/emails/process", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed"] == 0
        assert data["tickets_created"] == []


def test_process_emails_requires_admin(client, agent_headers):
    """Should reject non-admin users from processing emails."""
    response = client.post(
        "/api/v1/emails/process", headers=agent_headers
    )
    assert response.status_code == 403


def test_send_email_no_credentials(client, auth_headers):
    """Should return 500 when email credentials are not configured."""
    with patch(
        "src.services.email_service.settings"
    ) as mock_settings:
        mock_settings.MAIL_USERNAME = ""
        mock_settings.MAIL_PASSWORD = ""

        response = client.post(
            "/api/v1/emails/send",
            json={
                "to_email": "customer@example.com",
                "subject": "Test",
                "body": "Test body",
            },
            headers=auth_headers,
        )
        assert response.status_code == 500


def test_send_email_unauthenticated(client):
    """Should return 401 without a token."""
    response = client.post(
        "/api/v1/emails/send",
        json={
            "to_email": "customer@example.com",
            "subject": "Test",
            "body": "Test body",
        },
    )
    assert response.status_code == 401
