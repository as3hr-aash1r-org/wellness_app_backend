from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Date, Enum as SQLAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AppLevel(str, Enum):
    new_joiner = "new_joiner"
    prospect = "prospect"
    dxn_new = "dxn_new"
    guide = "guide"


class ConditionKey(str, Enum):
    orientation_read = "orientation_read"
    education_viewed = "education_viewed"
    products_viewed = "products_viewed"
    app_opened_3_days = "app_opened_3_days"


class UserLevelCondition(Base):
    __tablename__ = "user_level_conditions"
    __table_args__ = (
        UniqueConstraint('user_id', 'condition_key', name='uq_user_condition'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    condition_key: Mapped[ConditionKey] = mapped_column(SQLAEnum(ConditionKey), nullable=False)
    target_level: Mapped[AppLevel] = mapped_column(SQLAEnum(AppLevel), nullable=False)
    met_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="level_conditions")


class AppSession(Base):
    __tablename__ = "app_sessions"
    __table_args__ = (
        UniqueConstraint('user_id', 'session_date', name='uq_user_session_date'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="app_sessions")
