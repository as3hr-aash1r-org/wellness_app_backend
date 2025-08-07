from datetime import datetime, date
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Boolean, Date
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
    email: Mapped[str] = mapped_column(String, nullable=True,unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    sponsor_name: Mapped[str] = mapped_column(String, nullable=True)
    fcm_token: Mapped[str] = mapped_column(String, nullable=True) # Asher's code
    sponsor_code: Mapped[str] = mapped_column(String, nullable=True)
    distributor_code: Mapped[str] = mapped_column(String, nullable=True)
    # email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLAEnum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(),
                                                 nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    image_url : Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    
    # Expert-specific fields
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    position: Mapped[str] = mapped_column(String, nullable=True)
    dxn_distributor_number: Mapped[str] = mapped_column(String, nullable=True)
    
    # sponsor_code: Mapped[str] = mapped_column(String, nullable=True)
    # distributor_code: Mapped[str] = mapped_column(String, nullable=True)
    # is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
