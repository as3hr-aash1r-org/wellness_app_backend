from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class PasswordResetTokens(Base):
    __tablename__ = "password_reset_tokens"

    email = mapped_column(String, primary_key=True, index=True)
    otp = mapped_column(String, nullable=False)
    expires_at = mapped_column(DateTime, nullable=False)
    verified = mapped_column(Boolean, default=True)
