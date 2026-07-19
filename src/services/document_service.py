import os
import uuid as uuid_mod

from sqlalchemy.orm import Session

from src.core.logger import setup_logger
from src.models.document import Document
from src.services.ai_service import validate_document

logger = setup_logger(__name__)

UPLOAD_DIR = "uploads"


def save_document(
    db: Session,
    ticket_id: uuid_mod.UUID,
    filename: str,
    file_data: bytes,
    content_type: str,
) -> Document:
    """Save an uploaded document to disk and create a DB record."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate unique filename to prevent collisions
    unique_name = f"{uuid_mod.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(file_data)

    doc = Document(
        ticket_id=ticket_id,
        filename=filename,
        file_path=file_path,
        file_type=content_type,
        file_size=len(file_data),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"Saved document: {filename} for ticket {ticket_id}")
    return doc


def validate_ticket_documents(
    db: Session,
    ticket_id: uuid_mod.UUID,
    required_documents: list[str],
) -> dict:
    """Check which required documents are present and run AI validation."""
    documents = (
        db.query(Document).filter(Document.ticket_id == ticket_id).all()
    )

    submitted = [doc.filename for doc in documents]
    missing = [
        req
        for req in required_documents
        if not any(req.lower() in s.lower() for s in submitted)
    ]

    # AI-validate each document that hasn't been validated yet
    for doc in documents:
        if doc.is_valid is None:
            result = validate_document(doc.filename, doc.file_type)
            doc.is_valid = result.get("is_valid")
            doc.validation_notes = result.get("notes")

    db.commit()

    return {
        "ticket_id": str(ticket_id),
        "submitted_documents": [
            {
                "filename": d.filename,
                "is_valid": d.is_valid,
                "notes": d.validation_notes,
            }
            for d in documents
        ],
        "missing_documents": missing,
        "all_valid": (
            all(d.is_valid for d in documents) and len(missing) == 0
        ),
    }
