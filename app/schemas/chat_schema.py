from datetime import datetime
from typing import Optional, List, ForwardRef

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole
from app.schemas.user_schema import UserRead
from app.schemas.product_schema import ProductOut
from app.schemas.dxn_directory_schema import DXNDirectoryOut


class MessageBase(BaseModel):
    content: str
    image: Optional[str] = None


class MessageCreate(MessageBase):
    type: str  # text, audio, image, product, offices
    room_id: int
    sender_id: int
    product_id: Optional[int] = None  # For product messages
    office_id: Optional[int] = None   # For office messages

class MessageRead(MessageBase):
    id: int
    type: str
    room_id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    product_id: Optional[int] = None
    office_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class MessageWithDetails(MessageRead):
    """Message with product/office details included"""
    product: Optional[ProductOut] = None
    office: Optional[DXNDirectoryOut] = None
    
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
    PRODUCT = "product"
    OFFICES = "offices"
    JOIN = "join"
    LEAVE = "leave"
    ASSIGN_EXPERT = "assign_expert"
    ADMIN_JOIN = "admin_join"


class WSMessage(BaseModel):
    type: str  # Message type (text, audio, image, product, offices, join, leave, etc.)
    room_id: Optional[int] = None  # Chat room ID
    sender_id: int  # User ID of the sender
    content: Optional[str] = None  # Message content or caption for media
    sender_role: UserRole  # Role of the sender
    image: Optional[str] = None
    product_id: Optional[int] = None  # Product ID for product messages
    office_id: Optional[int] = None   # Office ID for office messages
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
    product_id: Optional[int] = None  # Product ID for product messages
    office_id: Optional[int] = None   # Office ID for office messages
    product: Optional[ProductOut] = None  # Product details for product messages
    office: Optional[DXNDirectoryOut] = None  # Office details for office messages
