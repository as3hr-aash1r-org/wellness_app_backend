from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime



class ProductStatus(str, Enum):
    published = "published"
    low_stock = "low stock"
    out_of_stock = "out of stock"


class ProductDimensions(BaseModel):
    """Product dimensions in centimeters"""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class ProductWeight(BaseModel):
    """Product weight and volume"""
    net_weight: Optional[float] = None  # in grams
    gross_weight: Optional[float] = None  # in grams
    volume: Optional[float] = None  # in ml or cubic cm


class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    company: Optional[str] = None
    product_group: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProductStatus] = ProductStatus.published
    category_id: int
    
    # Images
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Basic info
    tags: Optional[str] = None  # Comma-separated tags
    quantity: Optional[int] = 0
    best_seller: Optional[bool] = False
    
    # Dimensions (in cm)
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Weight & Volume
    net_weight: Optional[float] = None  # in grams
    gross_weight: Optional[float] = None  # in grams
    volume: Optional[float] = None  # in ml or cubic cm
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().upper() if v.strip() else None
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Clean up tags - remove extra spaces and ensure comma separation
            tags = [tag.strip() for tag in v.split(',') if tag.strip()]
            return ', '.join(tags) if tags else None
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Quantity cannot be negative')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    company: Optional[str] = None
    product_group: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProductStatus] = None
    category_id: Optional[int] = None
    
    # Images
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Basic info
    tags: Optional[str] = None
    quantity: Optional[int] = None
    best_seller: Optional[bool] = None
    
    # Dimensions
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Weight & Volume
    net_weight: Optional[float] = None
    gross_weight: Optional[float] = None
    volume: Optional[float] = None
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().upper() if v.strip() else None
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            tags = [tag.strip() for tag in v.split(',') if tag.strip()]
            return ', '.join(tags) if tags else None
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Quantity cannot be negative')
        return v


class ProductOut(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    company: Optional[str] = None
    product_group: Optional[str] = None
    description: Optional[str] = None
    status: ProductStatus
    category_id: int
    category_name: Optional[str] = None  # This will be populated by the API
    
    # Images
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Basic info
    tags: Optional[str] = None
    quantity: Optional[int] = None
    best_seller: Optional[bool] = None
    
    # Dimensions
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Weight & Volume
    net_weight: Optional[float] = None
    gross_weight: Optional[float] = None
    volume: Optional[float] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Category schemas
class ProductCategoryCreate(BaseModel):
    name: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip().title()


class ProductCategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
