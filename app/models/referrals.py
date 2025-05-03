from datetime import datetime

from sqlalchemy import Integer, String, func, DateTime, Boolean, Column
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Referrals(Base):
    __tablename__ = "referrals"
    id = mapped_column(Integer, primary_key=True)
    referral_code = mapped_column(String, nullable=False)
    referrer_user_id = mapped_column(Integer, nullable=False)
    referred_user_id = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
