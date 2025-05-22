from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from app.schemas.user_schema import UserAll, AdminRead


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    user_id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserAll

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: AdminRead

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class ForgetPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
