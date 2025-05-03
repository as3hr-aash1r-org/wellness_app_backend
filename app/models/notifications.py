from datetime import datetime

from sqlalchemy import Integer, String, func, DateTime, Boolean, Column
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Notifications(Base):
    __tablename__ = "notifications"
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String, nullable=False)
    body = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    target_user_id = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
