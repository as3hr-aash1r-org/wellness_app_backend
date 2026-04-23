from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FactTODPointer(Base):
    __tablename__ = "fact_tod_pointer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[FactType] = mapped_column(SQLAEnum(FactType), nullable=False, unique=True)
    current_fact_id: Mapped[int] = mapped_column(Integer, ForeignKey("facts.id", ondelete="SET NULL"), nullable=True)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    current_fact = relationship("Fact", foreign_keys=[current_fact_id])


class UserFactLibrary(Base):
    __tablename__ = "user_fact_library"
    __table_args__ = (
        UniqueConstraint('user_id', 'fact_id', name='uq_user_fact'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fact_id: Mapped[int] = mapped_column(Integer, ForeignKey("facts.id", ondelete="CASCADE"), nullable=False)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="fact_library")
    fact = relationship("Fact", backref="user_libraries")
