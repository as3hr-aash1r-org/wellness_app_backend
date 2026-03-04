from datetime import datetime, date
from enum import Enum

from sqlalchemy import Integer, DateTime, Enum as SQLAEnum, Boolean, Text, ForeignKey, String, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SubmissionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MediaType(str, Enum):
    image = "image"
    video = "video"
    reel = "reel"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    influencer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLAEnum(SubmissionStatus), 
        nullable=False, 
        default=SubmissionStatus.pending
    )
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    media: Mapped[list] = mapped_column(JSONB, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    expected_publication_date: Mapped[date] = mapped_column(Date, nullable=True)
    objective: Mapped[str] = mapped_column(Text, nullable=True)
    admin_feedback: Mapped[str] = mapped_column(Text, nullable=True)
    edited_by_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
