from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    phone_number: str
    role: UserRole


class UserInDB(UserBase):
    _id: int
    role: UserRole

    class Config:
        from_attributes = True


class User(UserInDB):
    pass
