from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.message import SenderType


class MessageCreate(BaseModel):
    content: str
    sender_type: SenderType = SenderType.AGENT


class MessageResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    sender_type: SenderType
    sender_email: Optional[str] = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
