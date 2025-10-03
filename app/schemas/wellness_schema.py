from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.wellness import WellnessType


class WellnessBase(BaseModel):
    title: str
    type: WellnessType
    steps: List[str]
    duration: str
    benefits: str

    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one step is required')
        if len(v) > 20:
            raise ValueError('Maximum 20 steps allowed')
        for step in v:
            if not step.strip():
                raise ValueError('Steps cannot be empty')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if not v.strip():
            raise ValueError('Duration cannot be empty')
        if len(v) > 50:
            raise ValueError('Duration cannot exceed 50 characters')
        return v.strip()

    @field_validator('benefits')
    @classmethod
    def validate_benefits(cls, v):
        if not v.strip():
            raise ValueError('Benefits cannot be empty')
        if len(v) > 1000:
            raise ValueError('Benefits cannot exceed 1000 characters')
        return v.strip()


class WellnessCreate(WellnessBase):
    pass


class WellnessUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[WellnessType] = None
    steps: Optional[List[str]] = None
    duration: Optional[str] = None
    benefits: Optional[str] = None

    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v):
        if v is not None:
            if not v or len(v) == 0:
                raise ValueError('At least one step is required')
            if len(v) > 20:
                raise ValueError('Maximum 20 steps allowed')
            for step in v:
                if not step.strip():
                    raise ValueError('Steps cannot be empty')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty')
            if len(v) > 200:
                raise ValueError('Title cannot exceed 200 characters')
            return v.strip()
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Duration cannot be empty')
            if len(v) > 50:
                raise ValueError('Duration cannot exceed 50 characters')
            return v.strip()
        return v

    @field_validator('benefits')
    @classmethod
    def validate_benefits(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Benefits cannot be empty')
            if len(v) > 1000:
                raise ValueError('Benefits cannot exceed 1000 characters')
            return v.strip()
        return v


class WellnessRead(WellnessBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WellnessStatsResponse(BaseModel):
    total_wellness: int
    exercise_count: int
    therapy_count: int
    stress_count: int
