from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.product_schema import ProductOut


class DesireListItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)


class DesireListItemUpdate(BaseModel):
    action: str = Field(..., pattern="^(increment|decrement)$")


class DesireListItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime
    product: ProductOut

    class Config:
        from_attributes = True


class DesireListCountResponse(BaseModel):
    count: int
