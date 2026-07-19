from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    subject: str
    customer_email: str
    customer_name: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    content: str  # First message content


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[UUID] = None
    intent: Optional[str] = None


class TicketResponse(BaseModel):
    id: UUID
    subject: str
    status: TicketStatus
    priority: TicketPriority
    intent: Optional[str] = None
    customer_email: str
    customer_name: Optional[str] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    total: int
    page: int
    per_page: int
