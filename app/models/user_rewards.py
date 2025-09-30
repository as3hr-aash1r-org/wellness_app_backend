from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RewardType(str, Enum):
    referral_bonus = "referral_bonus"
    signup_bonus = "signup_bonus"


class RewardStatus(str, Enum):
    active = "active"
    expired = "expired"
    used = "used"


class UserReward(Base):
    __tablename__ = "user_rewards"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    reward_type: Mapped[RewardType] = mapped_column(SQLAEnum(RewardType), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    discount_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[RewardStatus] = mapped_column(SQLAEnum(RewardStatus), nullable=False, default=RewardStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Reference to the referral that triggered this reward (if applicable)
    referral_id: Mapped[int] = mapped_column(Integer, ForeignKey("referrals.id"), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiration date if not provided (30 days from creation for referral bonuses)
        if not self.expires_at and self.reward_type == RewardType.referral_bonus:
            self.expires_at = self.created_at + timedelta(days=30)  # Referral rewards expire in 1 year
    
    @property
    def is_expired(self) -> bool:
        """Check if the reward has expired"""
        if self.status == RewardStatus.expired:
            return True
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    @property
    def is_active(self) -> bool:
        """Check if the reward is active and usable"""
        return self.status == RewardStatus.active and not self.is_expired
    
    def mark_as_used(self):
        """Mark the reward as used"""
        self.status = RewardStatus.used
        self.used_at = datetime.utcnow()
    
    def mark_as_expired(self):
        """Mark the reward as expired"""
        self.status = RewardStatus.expired
