"""Tests for document upload and listing endpoints."""
import io

import pytest


@pytest.fixture()
def auth_headers(client):
    """Helper: register a user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "doc_agent@example.com",
            "password": "password123",
            "full_name": "Doc Test Agent",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "doc_agent@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_ticket(client, auth_headers):
    """Helper: create a ticket and return its ID."""
    response = client.post(
        "/api/v1/tickets/",
        json={
            "subject": "Document test ticket",
            "customer_email": "customer@example.com",
            "content": "I need to submit my ID proof.",
        },
        headers=auth_headers,
    )
    return response.json()["id"]


def test_upload_document(client, auth_headers, sample_ticket):
    """Should upload a file and return document metadata."""
    file_content = b"This is a test document content."
    response = client.post(
        f"/api/v1/tickets/{sample_ticket}/documents",
        files={"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_doc.txt"
    assert data["file_type"] == "text/plain"
    assert data["file_size"] == len(file_content)
    assert data["ticket_id"] == sample_ticket


def test_upload_document_invalid_type(client, auth_headers, sample_ticket):
    """Should reject files with disallowed content types."""
    response = client.post(
        f"/api/v1/tickets/{sample_ticket}/documents",
        files={
            "file": (
                "malware.exe",
                io.BytesIO(b"fake binary"),
                "application/x-msdownload",
            )
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_upload_document_ticket_not_found(client, auth_headers):
    """Should return 404 when uploading to a non-existent ticket."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/tickets/{fake_id}/documents",
        files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_list_documents_empty(client, auth_headers, sample_ticket):
    """Should return empty list when no documents are uploaded."""
    response = client.get(
        f"/api/v1/tickets/{sample_ticket}/documents",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_documents_after_upload(client, auth_headers, sample_ticket):
    """Should list uploaded documents for a ticket."""
    # Upload 2 documents
    for name in ["id_proof.pdf", "address_proof.pdf"]:
        client.post(
            f"/api/v1/tickets/{sample_ticket}/documents",
            files={"file": (name, io.BytesIO(b"pdf content"), "application/pdf")},
            headers=auth_headers,
        )

    response = client.get(
        f"/api/v1/tickets/{sample_ticket}/documents",
        headers=auth_headers,
    )
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 2
    filenames = [d["filename"] for d in docs]
    assert "id_proof.pdf" in filenames
    assert "address_proof.pdf" in filenames


def test_documents_unauthenticated(client, sample_ticket):
    """Document endpoints should require authentication."""
    response = client.get(f"/api/v1/tickets/{sample_ticket}/documents")
    assert response.status_code == 401
