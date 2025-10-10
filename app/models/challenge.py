from datetime import datetime, timedelta, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from app.database.base import Base
from app.models.user_rewards import UserReward


class ChallengeType(str, Enum):
    gut = "gut"  
    nutrition = "nutrition"

class DurationType(str, Enum):
    minute = "minute"
    hour = "hour"
    day = "day"


class ChallengeStatus(str, Enum):
    pending = "pending"
    active = "active"
    completed = "completed"


class Challenge(Base):
    """Admin-created challenge templates"""
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[ChallengeType] = mapped_column(SQLAEnum(ChallengeType), nullable=False)
    
    # Challenge duration
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_type: Mapped[DurationType] = mapped_column(SQLAEnum(DurationType), nullable=False)
    
    # Reward configuration
    reward_time: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_time_type: Mapped[str] = mapped_column(String, nullable=False)  # 'hour' or 'day'
    
    # Admin fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_challenges = relationship("UserChallenge", back_populates="challenge")
    
    @property
    def duration_in_seconds(self) -> int:
        """Convert duration to seconds for automatic tracking"""
        if self.duration_type == DurationType.minute:
            return self.duration * 60
        elif self.duration_type == DurationType.hour:
            return self.duration * 3600
        else:  # day
            return self.duration * 86400
    
    @property
    def duration_display_text(self) -> str:
        """Get display text for duration (e.g., '7 Days', '2 Hours')"""
        unit = self.duration_type.value.title()
        if self.duration > 1:
            unit += "s"
        return f"{self.duration} {unit}"
    
    @property
    def reward_display_text(self) -> str:
        """Get display text for reward (e.g., '45 Days', '2 Hours')"""
        unit = self.reward_time_type.title()
        if self.reward_time > 1:
            unit += "s"
        return f"{self.reward_time} {unit}"


class UserChallenge(Base):
    """User's participation in a challenge"""
    __tablename__ = "user_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id: Mapped[int] = mapped_column(Integer, ForeignKey("challenges.id"), nullable=False)
    
    # Progress tracking
    status: Mapped[ChallengeStatus] = mapped_column(SQLAEnum(ChallengeStatus), nullable=False, default=ChallengeStatus.active)
    current_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Number of completed actions
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_progress_date: Mapped[date] = mapped_column(Date, nullable=True)  # Last date progress was updated
    last_progress_hour: Mapped[int] = mapped_column(Integer, nullable=True)  # Last hour progress was updated (0-23)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="user_challenges")
    user = relationship("User")
    
    def update_progress(self) -> dict:
        """Update progress manually (action-based)"""
        if self.status != ChallengeStatus.active:
            return {"success": False, "message": "Challenge is not active"}
        
        now = datetime.utcnow()
        current_date = now.date()
        current_hour = now.hour
        
        # Check if progress already updated for this period
        if self.challenge.duration_type == DurationType.day:
            if self.last_progress_date == current_date:
                return {"success": False, "message": "Progress for today is already updated"}
        elif self.challenge.duration_type == DurationType.hour:
            if (self.last_progress_date == current_date and 
                self.last_progress_hour == current_hour):
                return {"success": False, "message": "Progress for this hour is already updated"}
        
        # Update progress
        self.current_progress += 1
        self.last_progress_date = current_date
        if self.challenge.duration_type == DurationType.hour:
            self.last_progress_hour = current_hour
        
        # Calculate percentage
        self.progress_percentage = min((self.current_progress / self.challenge.duration) * 100, 100.0)
        # Auto-complete if target reached
        if self.current_progress >= self.challenge.duration:
            self.status = ChallengeStatus.completed
            self.completed_at = datetime.utcnow()
            
            return {"success": True, "message": "Challenge completed! 🎉", "completed": True}
        
        return {"success": True, "message": "Progress updated successfully!", "completed": False}
    
    @property
    def remaining_actions(self) -> int:
        """Get remaining actions needed to complete challenge"""
        if self.status == ChallengeStatus.completed:
            return 0
        return max(0, self.challenge.duration - self.current_progress)
    
    @property
    def progress_display_text(self) -> str:
        """Get progress display text (e.g., '5/7 days')"""
        try:
            if not self.challenge:
                return "0/0 days"
                
            # Now current_progress is the number of completed actions, not seconds
            current_count = self.current_progress
            total_count = self.challenge.duration
            
            if self.challenge.duration_type == DurationType.minute:
                unit = "minute" if total_count == 1 else "minutes"
            elif self.challenge.duration_type == DurationType.hour:
                unit = "hour" if total_count == 1 else "hours"
            else:  # day
                unit = "day" if total_count == 1 else "days"
                
            return f"{current_count}/{total_count} {unit}"
        except Exception as e:
            print(f"Error in progress_display_text: {e}")
            return "0/0 days"
    
    @property
    def is_completed(self) -> bool:
        """Check if challenge is completed"""
        return self.status == ChallengeStatus.completed
    
    @property
    def is_active(self) -> bool:
        """Check if challenge is active"""
        return self.status == ChallengeStatus.active
