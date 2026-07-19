from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user
from src.database.session import get_db
from src.models.ticket import TicketPriority, TicketStatus
from src.models.user import User
from src.schemas.message import MessageCreate, MessageResponse
from src.schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
)
from src.services.ticket_service import (
    add_message_to_ticket,
    create_ticket,
    get_ticket_by_id,
    get_ticket_messages,
    get_tickets,
    update_ticket,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket with an initial customer message."""
    return create_ticket(db, ticket_data)


@router.get("/", response_model=TicketListResponse)
def list_tickets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    assigned_to: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tickets with pagination and optional filters."""
    tickets, total = get_tickets(
        db, page, per_page, status, priority, assigned_to
    )
    return TicketListResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single ticket by ID."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: UUID,
    update_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ticket status, priority, assignment, or intent."""
    ticket = update_ticket(db, ticket_id, update_data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/{ticket_id}/messages", response_model=list[MessageResponse])
def list_messages(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the full conversation history for a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    messages = get_ticket_messages(db, ticket_id)
    return [MessageResponse.model_validate(m) for m in messages]


@router.post(
    "/{ticket_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    ticket_id: UUID,
    msg_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a reply to a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    message = add_message_to_ticket(
        db,
        ticket_id,
        msg_data.content,
        msg_data.sender_type,
        current_user.email,
    )
    return MessageResponse.model_validate(message)
