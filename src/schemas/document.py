from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    filename: str
    file_type: str
    file_size: int
    is_valid: Optional[bool] = None
    validation_notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentValidationRequest(BaseModel):
    ticket_id: UUID
    required_documents: list[str]
