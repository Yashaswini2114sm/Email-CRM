from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user, require_admin
from src.database.session import get_db
from src.models.ticket import TicketPriority
from src.models.user import User
from src.schemas.ticket import TicketCreate
from src.services.email_service import fetch_unread_emails, send_email
from src.services.ticket_service import create_ticket

router = APIRouter(prefix="/emails", tags=["Emails"])


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str


@router.post("/process")
def process_incoming_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Fetch unread emails from IMAP and create tickets. Admin only."""
    emails = fetch_unread_emails()

    created_tickets = []
    for parsed_email in emails:
        ticket_data = TicketCreate(
            subject=parsed_email.subject,
            customer_email=parsed_email.sender,
            priority=TicketPriority.MEDIUM,
            content=parsed_email.body,
        )
        ticket = create_ticket(db, ticket_data)
        created_tickets.append(str(ticket.id))

    return {
        "processed": len(emails),
        "tickets_created": created_tickets,
    }


@router.post("/send")
def send_outgoing_email(
    request: SendEmailRequest,
    current_user: User = Depends(get_current_user),
):
    """Send an email to a customer."""
    success = send_email(request.to_email, request.subject, request.body)
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to send email"
        )
    return {"status": "sent"}
