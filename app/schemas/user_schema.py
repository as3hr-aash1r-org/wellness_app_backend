from typing import Optional, Any, ClassVar
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    phone_number: str
    role: UserRole
    sponsor_code: Optional[str] = None
    distributor_code: Optional[str] = None

    @field_validator("sponsor_code", "distributor_code", mode="before")
    @classmethod
    def validate_codes(cls, v: Any, info):
        data = info.data
        role = data.get("role")

        if not role:
            return v

        if role == "sponsor":
            if info.field_name == "sponsor_code" and not v:
                raise ValueError("Sponsor code is required")
            if info.field_name == "distributor_code" and v:
                raise ValueError("Distributor code is not allowed")

        if role == "distributor":
            if info.field_name == "distributor_code" and not v:
                raise ValueError("Distributor code is required")
            if info.field_name == "sponsor_code" and not v:
                raise ValueError("Sponsor code is required")
        else:
            if info.field_name in ["sponsor_code", "distributor_code"]:
                raise ValueError(f"{role.capitalize()} should not provide {info.field_name.replace('_', ' ')}.")

        return v


class UserRead(UserBase):
    id: int
    phone_number: str
    role: UserRole
    sponsor_code: Optional[str] = None
    distributor_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserAll(UserRead):
    pass
