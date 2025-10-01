from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Enum as SQLAEnum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RewardType(str, Enum):
    referral_bonus = "referral_bonus"
    signup_bonus = "signup_bonus"
    challenge_reward = "challenge_reward"


class RewardTimeType(str, Enum):
    hour = "hour"
    day = "day"


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
    
    # Flexible reward time system
    reward_time: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount of time
    reward_time_type: Mapped[RewardTimeType] = mapped_column(SQLAEnum(RewardTimeType), nullable=False)  # hour or day
    
    status: Mapped[RewardStatus] = mapped_column(SQLAEnum(RewardStatus), nullable=False, default=RewardStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # References to source of reward
    referral_id: Mapped[int] = mapped_column(Integer, ForeignKey("referrals.id"), nullable=True)
    user_challenge_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_challenges.id"), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiration date based on reward time if not provided
        if not self.expires_at and self.reward_time is not None:
            if self.reward_time_type == RewardTimeType.hour:
                self.expires_at = self.created_at + timedelta(hours=self.reward_time)
            else:  # day
                self.expires_at = self.created_at + timedelta(days=self.reward_time)
    
    @property
    def reward_display_text(self) -> str:
        """Get display text for the reward (e.g., '45 Days', '2 Hours')"""
        # Handle legacy rewards that might not have reward_time set
        if self.reward_time is None or self.reward_time_type is None:
            return "30 Days"  # Default for legacy rewards
        
        unit = "Hour" if self.reward_time_type == RewardTimeType.hour else "Day"
        if self.reward_time > 1:
            unit += "s"
        return f"{self.reward_time} {unit}"
    
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
