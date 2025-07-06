from datetime import datetime
from typing import Optional, List, ForwardRef

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole
from app.schemas.user_schema import UserRead


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    type: str  # text, audio, image
    room_id: int
    sender_id: int

class MessageRead(MessageBase):
    id: int
    type: str
    room_id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True


class ChatRoomBase(BaseModel):
    name: Optional[str] = None


class ChatRoomCreate(ChatRoomBase):
    user_id: int
    expert_id: Optional[int] = None


class ChatRoomRead(ChatRoomBase):
    id: int
    user_id: int
    expert_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ChatRoomWithUser(ChatRoomRead):
    """Chat room with user details included"""
    user: UserRead
    
    class Config:
        from_attributes = True


class ChatRoomWithMessages(ChatRoomWithUser):
    """Chat room with messages and user details included"""
    messages: List[MessageRead] = []
    
    class Config:
        from_attributes = True


# WebSocket message schemas
class WSMessageType(str):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    JOIN = "join"
    LEAVE = "leave"
    ASSIGN_EXPERT = "assign_expert"
    ADMIN_JOIN = "admin_join"


class WSMessage(BaseModel):
    type: str  # Message type (text, audio, image, join, leave, etc.)
    room_id: Optional[int] = None  # Chat room ID
    sender_id: int  # User ID of the sender
    content: Optional[str] = None  # Message content or caption for media
    sender_role: UserRole  # Role of the sender
    timestamp: datetime = datetime.utcnow()  # Time when the message was sent

class WSResponse(BaseModel):
    type: str
    room_id: Optional[int] = None
    sender_id: int
    sender_name: str
    sender_role: UserRole
    content: Optional[str] = None
    timestamp: datetime
    message_id: Optional[int] = None  # Database ID of the message (if saved)
