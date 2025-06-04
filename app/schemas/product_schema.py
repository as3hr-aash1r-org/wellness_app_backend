from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime



class ProductStatus(str,Enum):
    published= "published"
    low_stock = "low stock"
    out_of_stock = "out of stock"

class ProductBase(BaseModel):
    name: str
    description: Optional[str]= None
    image_url :Optional[str]= None
    category_id:int
    status:Optional[ProductStatus]= ProductStatus.published


class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id:int
    created_at:datetime
    category_name:Optional[str]= None

    class Config:
        from_attributes = True