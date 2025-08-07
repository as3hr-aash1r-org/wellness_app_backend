from typing import Optional, Any, ClassVar, Literal
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole
from datetime import datetime, date


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    phone_number: str
    role: UserRole
    sponsor_code: Optional[str] = None
    distributor_code: Optional[str] = None
    sponsor_name: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None

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
    username: Optional[str]
    role: UserRole
    sponsor_name: Optional[str]
    sponsor_code: Optional[str]
    distributor_code: Optional[str]
    country: Optional[str]
    country_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    image_url: Optional[str]

    class Config:
        from_attributes = True

class UpdateProfilePictureRequest(BaseModel):
    image_url: str

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


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    sponsor_name: Optional[str] = None
    sponsor_code: Optional[str] = None
    distributor_code: Optional[str] = None
    fcm_token: Optional[str] = None


# Expert-specific schemas
class ExpertCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    password: str
    gender: Optional[Literal["male", "female", "other"]] = None
    position: Optional[str] = None
    country: Optional[str] = None
    dxn_distributor_number: Optional[str] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Basic phone number validation - you can make this more strict
        if not v or len(v.strip()) < 10:
            raise ValueError('Phone number must be at least 10 characters')
        return v.strip()


class ExpertRead(BaseModel):
    id: int
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    position: Optional[str]
    country: Optional[str]
    dxn_distributor_number: Optional[str]
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class ExpertUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    position: Optional[str] = None
    country: Optional[str] = None
    dxn_distributor_number: Optional[str] = None
