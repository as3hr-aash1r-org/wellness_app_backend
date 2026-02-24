from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.user_schema import UserCreate


class OTPRequest(BaseModel):
    phone_number: str
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Phone number is required')
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError('Phone number must be at least 10 characters')
        return cleaned


class OTPVerify(BaseModel):
    phone_number: str
    otp_code: str
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Phone number is required')
        return v.strip()
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        if not v or not v.strip():
            raise ValueError('OTP code is required')
        cleaned = v.strip()
        if not cleaned.isdigit():
            raise ValueError('OTP code must contain only digits')
        if len(cleaned) != 6:
            raise ValueError('OTP code must be 6 digits')
        return cleaned


class OTPVerifyWithRegistration(BaseModel):
    phone_number: str
    otp_code: str
    user_data: Optional[UserCreate] = None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Phone number is required')
        return v.strip()
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        if not v or not v.strip():
            raise ValueError('OTP code is required')
        cleaned = v.strip()
        if not cleaned.isdigit():
            raise ValueError('OTP code must contain only digits')
        if len(cleaned) != 6:
            raise ValueError('OTP code must be 6 digits')
        return cleaned
