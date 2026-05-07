from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class CardTypeCreate(BaseModel):
    type: str = Field(..., description="Card type name (e.g., fundamental, new_joiners)")


class CardTypeUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Card type name")


class CardTypeOut(BaseModel):
    id: int
    type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CardCreate(BaseModel):
    card_type_id: int = Field(..., description="Card type ID")
    content: str = Field(..., description="Raw HTML content")


class CardUpdate(BaseModel):
    card_type_id: Optional[int] = Field(None, description="Card type ID")
    content: Optional[str] = Field(None, description="Raw HTML content")


class CardOut(BaseModel):
    id: int
    card_type_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    card_type: Optional[CardTypeOut] = None

    model_config = {"from_attributes": True}

class CardTypeWithCards(BaseModel):
    id: int
    type: str
    created_at: datetime
    updated_at: datetime
    cards: List[CardOut] = []

    model_config = {"from_attributes": True}
