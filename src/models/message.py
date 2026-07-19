import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class SenderType(str, enum.Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    AI = "ai"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )
    sender_type: Mapped[SenderType] = mapped_column(
        SQLEnum(SenderType, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    sender_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Each message belongs to one ticket
    ticket = relationship("Ticket", back_populates="messages")
