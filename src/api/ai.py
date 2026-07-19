from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user
from src.database.session import get_db
from src.models.message import SenderType
from src.models.user import User
from src.schemas.document import DocumentValidationRequest
from src.schemas.ticket import TicketUpdate
from src.services.ai_service import detect_intent, generate_reply
from src.services.document_service import validate_ticket_documents
from src.services.ticket_service import (
    add_message_to_ticket,
    get_ticket_by_id,
    get_ticket_messages,
    update_ticket,
)

router = APIRouter(prefix="/ai", tags=["AI"])


class AnalyzeRequest(BaseModel):
    message: str
    ticket_id: UUID | None = None


class GenerateReplyRequest(BaseModel):
    ticket_id: UUID
    message: str | None = None


@router.post("/analyze")
def analyze_message(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detect customer intent from a message using AI."""
    result = detect_intent(request.message)

    # If ticket_id provided, save the detected intent on the ticket
    if request.ticket_id:
        update_ticket(
            db,
            request.ticket_id,
            TicketUpdate(intent=result.get("intent")),
        )

    return result


@router.post("/generate-reply")
def generate_ai_reply(
    request: GenerateReplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI reply for a ticket based on conversation context."""
    ticket = get_ticket_by_id(db, request.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Build conversation history for context
    messages = get_ticket_messages(db, request.ticket_id)
    history = [
        {"sender": msg.sender_type.value, "content": msg.content}
        for msg in messages
    ]

    # Use provided message or the last customer message
    customer_message = request.message
    if not customer_message:
        customer_msgs = [
            m for m in messages if m.sender_type == SenderType.CUSTOMER
        ]
        customer_message = (
            customer_msgs[-1].content if customer_msgs else ""
        )

    reply = generate_reply(
        customer_message, ticket.intent or "unknown", history
    )

    # Save the AI reply as a message on the ticket
    ai_message = add_message_to_ticket(
        db, request.ticket_id, reply, SenderType.AI
    )

    return {
        "reply": reply,
        "message_id": str(ai_message.id),
    }


@router.post("/validate-documents")
def validate_documents(
    request: DocumentValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate documents submitted for a ticket against requirements."""
    return validate_ticket_documents(
        db, request.ticket_id, request.required_documents
    )
