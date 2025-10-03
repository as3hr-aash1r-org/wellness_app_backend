from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database.base import Base


class WellnessType(str, Enum):
    exercise = "exercise"
    therapy = "therapy" 
    stress = "stress"


class Wellness(Base):
    """Wellness activities including Exercise, Sleep Therapy, and Stress Management"""
    __tablename__ = "wellness"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[WellnessType] = mapped_column(SQLAEnum(WellnessType), nullable=False)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)  # List of step strings
    duration: Mapped[str] = mapped_column(String, nullable=False)  # Simple string like "5 mins"
    benefits: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Wellness(id={self.id}, title='{self.title}', type='{self.type}')>"
