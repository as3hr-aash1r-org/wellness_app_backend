from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    image = "image"
    video = "video"
    reel = "reel"


class SubmissionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MediaItem(BaseModel):
    type: MediaType
    url: str
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        return v.strip()


class SubmissionCreate(BaseModel):
    caption: str
    tags: List[str] = []
    media: List[MediaItem]
    
    @field_validator('media')
    @classmethod
    def validate_media(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one media item is required')
        return v
    
    @field_validator('caption')
    @classmethod
    def validate_caption(cls, v):
        if not v or not v.strip():
            raise ValueError('Caption cannot be empty')
        return v.strip()


class SubmissionUpdate(BaseModel):
    caption: Optional[str] = None
    tags: Optional[List[str]] = None
    media: Optional[List[MediaItem]] = None
    
    @field_validator('media')
    @classmethod
    def validate_media(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('At least one media item is required')
        return v


class SubmissionReject(BaseModel):
    feedback: str
    
    @field_validator('feedback')
    @classmethod
    def validate_feedback(cls, v):
        if not v or not v.strip():
            raise ValueError('Feedback is required when rejecting')
        return v.strip()


class SubmissionRead(BaseModel):
    id: int
    influencer_id: int
    status: SubmissionStatus
    caption: str
    tags: List[str]
    media: List[MediaItem]
    admin_feedback: Optional[str]
    edited_by_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
