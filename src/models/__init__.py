from src.models.user import User, UserRole
from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.message import Message, SenderType
from src.models.document import Document

# Importing all models here ensures Alembic can discover them for migrations
__all__ = [
    "User", "UserRole",
    "Ticket", "TicketStatus", "TicketPriority",
    "Message", "SenderType",
    "Document",
]
