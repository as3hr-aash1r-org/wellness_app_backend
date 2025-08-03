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
    content: Optional[str] = None  # Detailed content
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None  # For video thumbnails
    type: FeedType
    category_id: Optional[int] = None
    tags: Optional[str] = None  # Comma-separated tags
    author: Optional[str] = None
    source: Optional[str] = None
    is_featured: Optional[bool] = False

class FeedCreate(FeedBase):
    pass

class FeedOut(FeedBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FeedCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

class FeedCategoryCreate(FeedCategoryBase):
    pass

class FeedCategoryOut(FeedCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
