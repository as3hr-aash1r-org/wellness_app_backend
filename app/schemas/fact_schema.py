from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.fact import FactType


class FactBase(BaseModel):
    title: str
    description: str
    type: FactType


class FactCreate(FactBase):
    is_tod: Optional[bool] = False


class FactUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[FactType] = None
    is_tod: Optional[bool] = None


class FactRead(FactBase):
    id: int
    is_tod: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FactInDB(FactRead):
    pass
