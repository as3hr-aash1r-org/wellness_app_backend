from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.support_ticket import TicketStatus


class SupportTicketCreate(BaseModel):
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., description="Ticket description")
    file_url: Optional[str] = Field(None, description="Firebase file URL (optional)")


class SupportTicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    description: str
    file_url: Optional[str] = None
    status: TicketStatus
    admin_reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminReplyRequest(BaseModel):
    admin_reply: str = Field(..., description="Admin's reply to the ticket")
