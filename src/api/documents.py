from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.schemas.document import DocumentResponse
from src.services.document_service import save_document
from src.services.ticket_service import get_ticket_by_id

router = APIRouter(prefix="/tickets", tags=["Documents"])

# Allowed file types to prevent malicious uploads
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/{ticket_id}/documents",
    response_model=DocumentResponse,
    status_code=201,
)
async def upload_document(
    ticket_id: UUID,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document attachment to a ticket.

    Accepts PDF, images (JPEG/PNG/WebP), Word documents, and plain text.
    Maximum file size: 10 MB.
    """
    # Verify the ticket exists
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. "
            f"Allowed: PDF, JPEG, PNG, WebP, Word, TXT",
        )

    # Read file data and check size
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    # Save via the document service
    document = save_document(
        db=db,
        ticket_id=ticket_id,
        filename=file.filename or "unnamed",
        file_data=file_data,
        content_type=file.content_type or "application/octet-stream",
    )

    return DocumentResponse.model_validate(document)


@router.get(
    "/{ticket_id}/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents attached to a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    from src.models.document import Document

    documents = (
        db.query(Document)
        .filter(Document.ticket_id == ticket_id)
        .order_by(Document.created_at.asc())
        .all()
    )
    return [DocumentResponse.model_validate(d) for d in documents]
