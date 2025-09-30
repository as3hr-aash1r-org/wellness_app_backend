from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FactType(str, Enum):
    gut = "gut"
    nutrition = "nutrition"
    sleep = "sleep"


class Fact(Base):
    __tablename__ = "facts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[FactType] = mapped_column(SQLAEnum(FactType), nullable=False)
    is_tod: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Tip of the day
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
