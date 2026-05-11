from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.card import Card, CardType
from app.schemas.card_schema import CardCreate, CardUpdate, CardTypeCreate, CardTypeUpdate


# ==================== CardType CRUD ====================

class CRUDCardType:
    def create(self, db: Session, *, obj_in: CardTypeCreate) -> CardType:
        """Create a new card type"""
        # Check if type already exists
        existing = self.get_by_type(db, type_name=obj_in.type)
        if existing:
            raise HTTPException(status_code=400, detail=f"Card type '{obj_in.type}' already exists")
        
        card_type = CardType(type=obj_in.type)
        db.add(card_type)
        db.commit()
        db.refresh(card_type)
        return card_type
    
    def get_by_id(self, db: Session, *, card_type_id: int) -> Optional[CardType]:
        """Get card type by ID"""
        query = select(CardType).where(CardType.id == card_type_id)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_type(self, db: Session, *, type_name: str) -> Optional[CardType]:
        """Get card type by type name"""
        query = select(CardType).where(CardType.type == type_name)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[CardType]:
        """Get all card types"""
        query = select(CardType).order_by(CardType.type).offset(skip).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())
    
    def update(self, db: Session, *, card_type_id: int, obj_in: CardTypeUpdate) -> CardType:
        """Update a card type"""
        card_type = self.get_by_id(db, card_type_id=card_type_id)
        if not card_type:
            raise HTTPException(status_code=404, detail="Card type not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Check if new type name already exists
        if 'type' in update_data:
            existing = self.get_by_type(db, type_name=update_data['type'])
            if existing and existing.id != card_type_id:
                raise HTTPException(status_code=400, detail=f"Card type '{update_data['type']}' already exists")
        
        for field, value in update_data.items():
            setattr(card_type, field, value)
        
        card_type.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(card_type)
        return card_type
    
    def delete(self, db: Session, *, card_type_id: int) -> bool:
        """Delete a card type (cascades to cards)"""
        card_type = self.get_by_id(db, card_type_id=card_type_id)
        if not card_type:
            raise HTTPException(status_code=404, detail="Card type not found")
        
        db.delete(card_type)
        db.commit()
        return True


# ==================== Card CRUD ====================

class CRUDCard:
    def create(self, db: Session, *, obj_in: CardCreate) -> Card:
        """Create a new card"""
        # Verify card type exists
        card_type_crud.get_by_id(db, card_type_id=obj_in.card_type_id)
        if not card_type_crud.get_by_id(db, card_type_id=obj_in.card_type_id):
            raise HTTPException(status_code=404, detail="Card type not found")
        
        card = Card(
            card_type_id=obj_in.card_type_id,
            content=obj_in.content
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        return card
    
    def get_by_id(self, db: Session, *, card_id: int) -> Optional[Card]:
        """Get card by ID"""
        query = select(Card).where(Card.id == card_id)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_type_id(self, db: Session, *, card_type_id: int) -> List[Card]:
        """Get all cards by card type ID (oldest first for swiper)"""
        query = select(Card).where(Card.card_type_id == card_type_id).order_by(Card.created_at.asc())
        result = db.execute(query)
        return list(result.scalars().all())
    
    def get_by_type_name(self, db: Session, *, type_name: str) -> List[Card]:
        """Get all cards by card type name"""
        card_type = card_type_crud.get_by_type(db, type_name=type_name)
        if not card_type:
            return []
        return self.get_by_type_id(db, card_type_id=card_type.id)
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Card]:
        """Get all cards (oldest first for swiper)"""
        query = select(Card).order_by(Card.created_at.asc()).offset(skip).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())
    
    def update(self, db: Session, *, card_id: int, obj_in: CardUpdate) -> Card:
        """Update a card"""
        card = self.get_by_id(db, card_id=card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Verify new card type exists if being updated
        if 'card_type_id' in update_data:
            if not card_type_crud.get_by_id(db, card_type_id=update_data['card_type_id']):
                raise HTTPException(status_code=404, detail="Card type not found")
        
        for field, value in update_data.items():
            setattr(card, field, value)
        
        card.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(card)
        return card
    
    def delete(self, db: Session, *, card_id: int) -> bool:
        """Delete a card"""
        card = self.get_by_id(db, card_id=card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        db.delete(card)
        db.commit()
        return True


card_type_crud = CRUDCardType()
card_crud = CRUDCard()
