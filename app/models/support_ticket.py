from datetime import datetime
from enum import Enum
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TicketStatus(str, Enum):
    pending = "Pending"
    answered = "Answered"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=True)  # Optional file attachment
    status: Mapped[TicketStatus] = mapped_column(SQLAEnum(TicketStatus), nullable=False, default=TicketStatus.pending)
    admin_reply: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="support_tickets")
