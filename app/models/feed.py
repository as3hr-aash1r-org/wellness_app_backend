from datetime import datetime

from sqlalchemy import Integer, String, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Feeds(Base):
    __tablename__ = "feeds"
    id = mapped_column(Integer, primary_key=True)
    content = mapped_column(Text, nullable=False)
    title = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)  # enum
    media_url = mapped_column(String, nullable=True)
    status = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
