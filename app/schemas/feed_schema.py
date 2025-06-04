from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class FeedType(str, Enum):
    post = "post"
    video = "video"
    reel = "reel"

class FeedBase(BaseModel):
    title: str
    description: Optional[str] = None
    media_url: Optional[str] = None
    type: FeedType

class FeedCreate(FeedBase):
    pass

class FeedOut(FeedBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
