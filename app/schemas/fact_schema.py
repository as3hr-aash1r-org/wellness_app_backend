from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.fact import FactType


class FactBase(BaseModel):
    title: str
    description: str
    type: FactType


class FactCreate(FactBase):
    pass


class FactUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[FactType] = None


class FactRead(FactBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FactInDB(FactRead):
    pass


# Bulk upload schemas
class BulkUploadError(BaseModel):
    row: int
    reason: str


class BulkUploadResponse(BaseModel):
    total_rows: int
    inserted: int
    failed: int
    errors: list[BulkUploadError]


# User fact library schemas
class UserFactLibraryOut(BaseModel):
    id: int
    user_id: int
    fact_id: int
    saved_at: datetime
    fact: FactRead

    class Config:
        from_attributes = True
