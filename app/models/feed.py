from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum

class FeedType(enum.Enum):
    post = "post"
    video = "video"
    reel = "reel"

class FeedCategory(Base):
    __tablename__ = "feed_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    feed_items = relationship("FeedItem", back_populates="category")

class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Full content for detailed posts
    type = Column(Enum(FeedType), nullable=False)
    media_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)  # For video thumbnails or post images
    category_id = Column(Integer, ForeignKey("feed_categories.id"), nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    author = Column(String, nullable=True)
    source = Column(String, nullable=True)  # Source of information like "healthline.com"
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    category = relationship("FeedCategory", back_populates="feed_items")
    
