from pydantic import BaseModel, EmailStr
from typing import Optional

class DXNDirectoryBase(BaseModel):
    country: str
    person: str
    position: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    whatsapp1: Optional[str] = None
    whatsapp2: Optional[str] = None
    email1: Optional[EmailStr] = None
    email2: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province_state: Optional[str] = None
    price_list: Optional[str] = None

class DXNDirectoryCreate(DXNDirectoryBase):
    pass

class DXNDirectoryUpdate(DXNDirectoryBase):
    pass

class DXNDirectoryOut(DXNDirectoryBase):
    id: int
    class Config:
        from_attributes = True
