import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, values_callable=lambda obj: [e.value for e in obj]), default=TicketStatus.OPEN
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLEnum(TicketPriority, values_callable=lambda obj: [e.value for e in obj]), default=TicketPriority.MEDIUM
    )
    intent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    assignee = relationship("User", back_populates="assigned_tickets")
    messages = relationship(
        "Message", back_populates="ticket", order_by="Message.created_at"
    )
    documents = relationship("Document", back_populates="ticket")
