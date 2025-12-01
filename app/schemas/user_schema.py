from typing import Optional, Any, ClassVar, Literal
from pydantic import BaseModel, EmailStr, field_validator
from pydantic import BaseModel, EmailStr, field_validator, model_validator
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
    country: str  # Required: Country name sent from frontend
    country_code: str  # Required: Country code sent from frontend
    country_code: str  # Required: 2-letter ISO Country code (e.g. PK, US)
    phone_code: str # Required: International dialing code (e.g. +92)
    referral_code: Optional[str] = None  # Optional referral code for signup
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        if not v or not v.strip():
            raise ValueError('Country is required')
        if len(v.strip()) < 2:
            raise ValueError('Country name must be at least 2 characters')
        if len(v.strip()) > 100:
            raise ValueError('Country name cannot exceed 100 characters')
        return v.strip()
    
    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Country code is required')
        # Basic validation for country code format (+XX or +XXX)
        
        cleaned = v.strip()
        
        # Strict validation: Must be 2-letter ISO code (e.g., PK, US)
        if len(cleaned) == 2 and cleaned.isalpha() and cleaned.isupper():
            return cleaned
            
        raise ValueError('Country code must be a 2-letter ISO code (e.g., PK, US)')
    @field_validator('phone_code')
    @classmethod
    def validate_phone_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Phone code is required')
            
        cleaned = v.strip()
        if not cleaned.startswith('+'):
            raise ValueError('Country code must start with +')
        if len(cleaned) < 2 or len(cleaned) > 5:
            raise ValueError('Country code must be between 2-5 characters (including +)')
            raise ValueError('Phone code must start with +')
            
        if len(cleaned) < 2 or len(cleaned) > 6:
            raise ValueError('Phone code must be between 2-6 characters (including +)')
            
        if not cleaned[1:].isdigit():
            raise ValueError('Country code must contain only digits after +')
            raise ValueError('Phone code must contain only digits after +')
            
        return cleaned
    @model_validator(mode='after')
    def validate_country_consistency(self):
        from app.utils.country_utils import CountryValidator
        
        try:
            CountryValidator.validate_consistency(
                country_name=self.country,
                country_code=self.country_code,
                phone_code=self.phone_code,
                phone_number=self.phone_number
            )
        except ValueError as e:
            raise ValueError(str(e))
            
        return self
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
    gender: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    image_url: Optional[str]
    referral_code: Optional[str]
    distributor_rank: Optional[str]
    member_name: Optional[str]
    sponsor_rank: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    class Config:
        from_attributes = True
class UpdateProfilePictureRequest(BaseModel):
    image_url: str
class ProfileUpdateRequest(BaseModel):
    """Profile update request - only editable fields"""
    # Profile section - only username is editable
    username: Optional[str] = None
    
    # DXN Member section - all editable except rank
    sponsor_name: Optional[str] = None  # Member name in DXN card
    distributor_code: Optional[str] = None  # Distributor no.
    sponsor_code: Optional[str] = None  # Sponsor no.
    distributor_rank: Optional[str] = None  # Distributor rank
    member_name: Optional[str] = None  # Member name in DXN card
    sponsor_rank: Optional[str] = None  # Sponsor rank
    email: Optional[str] = None  # Email
    gender: Optional[str] = None  # Gender
    
    # Profile photo
    image_url: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Username cannot be empty')
            if len(v.strip()) < 2:
                raise ValueError('Username must be at least 2 characters long')
            if len(v.strip()) > 50:
                raise ValueError('Username cannot exceed 50 characters')
            return v.strip()
        return v
    
    @field_validator('sponsor_name')
    @classmethod
    def validate_sponsor_name(cls, v):
        if v is not None:
            if len(v.strip()) > 100:
                raise ValueError('Sponsor name cannot exceed 100 characters')
            return v.strip() if v.strip() else None
        return v
    
    @field_validator('distributor_code')
    @classmethod
    def validate_distributor_code(cls, v):
        if v is not None:
            if len(v.strip()) > 20:
                raise ValueError('Distributor code cannot exceed 20 characters')
            return v.strip() if v.strip() else None
        return v
    
    @field_validator('sponsor_code')
    @classmethod
    def validate_sponsor_code(cls, v):
        if v is not None:
            if len(v.strip()) > 20:
                raise ValueError('Sponsor code cannot exceed 20 characters')
            return v.strip() if v.strip() else None
        return v
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
