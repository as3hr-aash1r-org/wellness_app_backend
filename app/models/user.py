from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    expert = "expert"
    official = "official"
    guest = "guest"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    sponsor_name: Mapped[str] = mapped_column(String, nullable=True)
    sponsor_code: Mapped[str] = mapped_column(String, nullable=True)
    distributor_code: Mapped[str] = mapped_column(String, nullable=True)
    # email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLAEnum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(),
                                                 nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    # sponsor_code: Mapped[str] = mapped_column(String, nullable=True)
    # distributor_code: Mapped[str] = mapped_column(String, nullable=True)
    # is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
