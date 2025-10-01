from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.models.challenge import ChallengeType, DurationType, ChallengeStatus


class ChallengeBase(BaseModel):
    title: str
    description: str
    type: ChallengeType
    duration: int
    duration_type: DurationType
    reward_time: int
    reward_time_type: str  # 'hour' or 'day'


class ChallengeCreate(ChallengeBase):
    @field_validator('reward_time_type')
    @classmethod
    def validate_reward_time_type(cls, v):
        if v not in ['hour', 'day']:
            raise ValueError('reward_time_type must be either "hour" or "day"')
        return v
    
    @field_validator('reward_time')
    @classmethod
    def validate_reward_time(cls, v, info):
        reward_time_type = info.data.get('reward_time_type')
        
        if reward_time_type == 'hour':
            if v < 1:
                raise ValueError('Reward time cannot be less than 1 hour')
            if v > 24:
                raise ValueError('Reward time cannot be more than 24 hours. Use days instead.')
        elif reward_time_type == 'day':
            if v < 1:
                raise ValueError('Reward time cannot be less than 1 day')
        
        return v


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ChallengeType] = None
    duration: Optional[int] = None
    duration_type: Optional[DurationType] = None
    reward_time: Optional[int] = None
    reward_time_type: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('reward_time_type')
    @classmethod
    def validate_reward_time_type(cls, v):
        if v is not None and v not in ['hour', 'day']:
            raise ValueError('reward_time_type must be either "hour" or "day"')
        return v
    
    @field_validator('reward_time')
    @classmethod
    def validate_reward_time(cls, v, info):
        if v is not None:
            reward_time_type = info.data.get('reward_time_type')
            
            if reward_time_type == 'hour':
                if v < 1:
                    raise ValueError('Reward time cannot be less than 1 hour')
                if v > 24:
                    raise ValueError('Reward time cannot be more than 24 hours. Use days instead.')
            elif reward_time_type == 'day':
                if v < 1:
                    raise ValueError('Reward time cannot be less than 1 day')
        return v


class ChallengeRead(ChallengeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    status: str
    duration_display_text: str
    reward_display_text: str

    class Config:
        from_attributes = True


class UserChallengeBase(BaseModel):
    challenge_id: int


class UserChallengeCreate(UserChallengeBase):
    pass


class UserChallengeRead(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    status: ChallengeStatus
    current_progress: int
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    remaining_actions: int
    progress_display_text: str
    is_completed: bool
    is_active: bool
    
    # Progress tracking fields
    last_progress_date: Optional[str] = None  # ISO date string
    last_progress_hour: Optional[int] = None
    
    # Challenge details
    # challenge: ChallengeRead

    class Config:
        from_attributes = True


class UserChallengeUpdate(BaseModel):
    status: Optional[ChallengeStatus] = None


class ChallengeStatsResponse(BaseModel):
    total_challenges: int
    active_challenges: int
    completed_challenges: int
    total_rewards_earned: int


class RewardSummaryResponse(BaseModel):
    total_active_rewards: int
    total_reward_time_hours: int
    total_reward_time_days: int
    rewards: List[dict]  # List of reward details
