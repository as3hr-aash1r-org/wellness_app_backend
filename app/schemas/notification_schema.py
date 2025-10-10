from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    body: str
    type: str
    target_user_id: int

class NotificationCreate(NotificationBase):
    sender_id: Optional[int] = None

class SenderOut(BaseModel):
    id: int
    username: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationOut(NotificationBase):
    id: int
    created_at: datetime
    sender: Optional[SenderOut] = None

    class Config:
        from_attributes = True

class BroadcastNotificationRequest(BaseModel):
    title: str
    body: str
    role_filter: Optional[str] = None
