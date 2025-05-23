from typing import Optional, Any, ClassVar
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    phone_number: str
    role: UserRole
    sponsor_code: Optional[str] = None
    distributor_code: Optional[str] = None
    sponsor_name: Optional[str] = None

    # @field_validator("role")
    # def normalize_role(cls, v):
    #     if isinstance(v, str):
    #         v = v.upper()
    #     return v

    # @field_validator("role")
    # @classmethod
    # def validate_official_fields(cls,v:Any,info):
    #     data = info.data
    #     role = data.get("role")
    #     if role == UserRole.OFFICIAL:
    #         missing_fields = [f for f in ['sponsor_name', 'distributor_code', 'sponsor_code'] if not data.get(f)]
    #         if missing_fields:
    #             raise ValueError(f"Missing required fields for dxn member: {', '.join(missing_fields)}")
    #     return v
    


class UserLogin(BaseModel):
    phone_number: str


class UserRead(BaseModel):
    id: int
    phone_number: Optional[str]
    role: UserRole
    sponsor_name: Optional[str]
    sponsor_code: Optional[str]
    distributor_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserAll(UserRead):
    pass


class FCMTokenUpdate(BaseModel):
    fcm_token: str
