from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.sql import func
from app.database.base import Base
import enum

class FeedType(enum.Enum):
    post = "post"
    video = "video"
    reel = "reel"

class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(FeedType), nullable=False)
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
