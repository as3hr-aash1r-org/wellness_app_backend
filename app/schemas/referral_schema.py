from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InviteeDetails(BaseModel):
    user_id: int
    g_id: Optional[str]
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    country: Optional[str]
    image_url: Optional[str]
    joined_at: datetime
    referral_code: Optional[str]
    
    class Config:
        from_attributes = True


class InviteListResponse(BaseModel):
    invitees: list[InviteeDetails]
    total_invites: int
    current_page: int
    page_size: int
    total_pages: int
