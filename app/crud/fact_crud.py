from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from app.models.fact import Fact, FactType
from app.schemas.fact_schema import FactCreate, FactUpdate


class CRUDFact:
    def create_fact(self, db: Session, *, obj_in: FactCreate) -> Fact:
        """Create a new fact with tip-of-the-day logic"""
        
        # If this fact is being set as tip of the day, unset any existing tip of the day for this type
        if obj_in.is_tod:
            self._unset_existing_tod(db, fact_type=obj_in.type)
        
        db_obj = Fact(
            title=obj_in.title,
            description=obj_in.description,
            type=obj_in.type,
            is_tod=obj_in.is_tod
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_fact_by_id(self, db: Session, *, fact_id: int) -> Optional[Fact]:
        """Get a fact by ID"""
        query = select(Fact).where(Fact.id == fact_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_facts_by_type(self, db: Session, *, fact_type: FactType, skip: int = 0, limit: int = 100) -> List[Fact]:
        """Get all facts by type with pagination"""
        query = select(Fact).where(Fact.type == fact_type).offset(skip).limit(limit).order_by(Fact.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_facts_by_type(self, db: Session, *, fact_type: FactType) -> int:
        """Count facts by type"""
        query = select(func.count(Fact.id)).where(Fact.type == fact_type)
        result = db.execute(query)
        return result.scalar()

    def get_all_facts(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Fact]:
        """Get all facts with pagination"""
        query = select(Fact).offset(skip).limit(limit).order_by(Fact.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_all_facts(self, db: Session) -> int:
        """Count all facts"""
        query = select(func.count(Fact.id))
        result = db.execute(query)
        return result.scalar()

    def get_tip_of_the_day(self, db: Session, *, fact_type: FactType) -> Optional[Fact]:
        """Get the current tip of the day for a specific type"""
        query = select(Fact).where(
            and_(Fact.type == fact_type, Fact.is_tod == True)
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    def update_fact(self, db: Session, *, fact_id: int, obj_in: FactUpdate) -> Fact:
        """Update a fact with tip-of-the-day logic"""
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        # If this fact is being set as tip of the day, unset any existing tip of the day for this type
        if update_data.get("is_tod") is True:
            # Get the fact type (either from update data or existing fact)
            fact_type = update_data.get("type", fact.type)
            self._unset_existing_tod(db, fact_type=fact_type, exclude_fact_id=fact_id)

        # Apply updates
        for field, value in update_data.items():
            if hasattr(fact, field):
                setattr(fact, field, value)

        db.commit()
        db.refresh(fact)
        return fact

    def delete_fact(self, db: Session, *, fact_id: int) -> Fact:
        """Delete a fact"""
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")

        db.delete(fact)
        db.commit()
        return fact

    def set_tip_of_the_day(self, db: Session, *, fact_id: int) -> Fact:
        """Set a specific fact as tip of the day for its type"""
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")

        # Unset existing tip of the day for this type
        self._unset_existing_tod(db, fact_type=fact.type, exclude_fact_id=fact_id)
        
        # Set this fact as tip of the day
        fact.is_tod = True
        db.commit()
        db.refresh(fact)
        return fact

    def _unset_existing_tod(self, db: Session, *, fact_type: FactType, exclude_fact_id: Optional[int] = None):
        """Private method to unset existing tip of the day for a specific type"""
        query = select(Fact).where(
            and_(Fact.type == fact_type, Fact.is_tod == True)
        )
        
        if exclude_fact_id:
            query = query.where(Fact.id != exclude_fact_id)
        
        result = db.execute(query)
        existing_tod_facts = result.scalars().all()
        
        for tod_fact in existing_tod_facts:
            tod_fact.is_tod = False
        
        db.commit()

    def get_facts_count_by_type(self, db: Session, *, fact_type: FactType) -> int:
        """Get count of facts by type"""
        query = select(Fact).where(Fact.type == fact_type)
        result = db.execute(query)
        return len(result.scalars().all())


fact_crud = CRUDFact()
