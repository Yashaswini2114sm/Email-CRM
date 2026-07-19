from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.logger import setup_logger
from src.models.message import Message, SenderType
from src.models.ticket import Ticket, TicketPriority, TicketStatus
from src.schemas.ticket import TicketCreate, TicketUpdate

logger = setup_logger(__name__)


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    """Create a new support ticket with its first customer message."""
    ticket = Ticket(
        subject=ticket_data.subject,
        customer_email=ticket_data.customer_email,
        customer_name=ticket_data.customer_name,
        priority=ticket_data.priority,
    )
    db.add(ticket)
    db.flush()  # Get the ticket ID without committing yet

    # Create the first message from the customer
    first_message = Message(
        ticket_id=ticket.id,
        sender_type=SenderType.CUSTOMER,
        sender_email=ticket_data.customer_email,
        content=ticket_data.content,
    )
    db.add(first_message)
    db.commit()
    db.refresh(ticket)
    logger.info(f"Created ticket: {ticket.id} — {ticket.subject}")
    return ticket


def get_tickets(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    assigned_to: Optional[UUID] = None,
) -> tuple[list[Ticket], int]:
    """Fetch paginated tickets with optional filters."""
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)

    total = query.count()
    tickets = (
        query.order_by(Ticket.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return tickets, total


def get_ticket_by_id(db: Session, ticket_id: UUID) -> Ticket | None:
    """Fetch a single ticket by ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket(
    db: Session, ticket_id: UUID, update_data: TicketUpdate
) -> Ticket | None:
    """Update ticket fields. Only updates fields that were explicitly set."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)
    logger.info(f"Updated ticket: {ticket.id}")
    return ticket


def add_message_to_ticket(
    db: Session,
    ticket_id: UUID,
    content: str,
    sender_type: SenderType,
    sender_email: Optional[str] = None,
) -> Message:
    """Add a new message to an existing ticket's conversation."""
    message = Message(
        ticket_id=ticket_id,
        sender_type=sender_type,
        sender_email=sender_email,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_ticket_messages(db: Session, ticket_id: UUID) -> list[Message]:
    """Get all messages for a ticket, ordered chronologically."""
    return (
        db.query(Message)
        .filter(Message.ticket_id == ticket_id)
        .order_by(Message.created_at.asc())
        .all()
    )
