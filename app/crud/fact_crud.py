from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, and_, func, cast, Date
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date

from app.models.fact import Fact, FactType, FactTODPointer, UserFactLibrary
from app.schemas.fact_schema import FactCreate, FactUpdate


class CRUDFact:
    def create_fact(self, db: Session, *, obj_in: FactCreate) -> Fact:
        """Create a new fact"""
        db_obj = Fact(
            title=obj_in.title,
            description=obj_in.description,
            type=obj_in.type
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # If this is the first fact of this type, initialize the pointer
        self._initialize_pointer_if_needed(db, fact_type=obj_in.type)
        
        return db_obj

    def get_fact_by_id(self, db: Session, *, fact_id: int) -> Optional[Fact]:
        """Get a fact by ID"""
        query = select(Fact).where(Fact.id == fact_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_facts_by_type(self, db: Session, *, fact_type: FactType, skip: int = 0, limit: int = 100) -> List[Fact]:
        """Get all facts by type with pagination"""
        query = select(Fact).where(Fact.type == fact_type).offset(skip).limit(limit).order_by(Fact.id.asc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_facts_by_type(self, db: Session, *, fact_type: FactType) -> int:
        """Count facts by type"""
        query = select(func.count(Fact.id)).where(Fact.type == fact_type)
        result = db.execute(query)
        return result.scalar()

    def get_all_facts(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Fact]:
        """Get all facts with pagination"""
        query = select(Fact).offset(skip).limit(limit).order_by(Fact.id.asc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_all_facts(self, db: Session) -> int:
        """Count all facts"""
        query = select(func.count(Fact.id))
        result = db.execute(query)
        return result.scalar()

    def get_tip_of_the_day(self, db: Session, *, fact_type: FactType, user_id: int) -> Optional[Fact]:
        """
        Get the current tip of the day for a specific type.
        Returns None if user has already saved ANY fact of this type TODAY (UTC).
        Strictly 1 tip per day per type.
        """
        # Get today's date in UTC
        today_utc = datetime.utcnow().date()
        
        # Check if user saved any fact of this type today (UTC date comparison)
        saved_today_query = select(UserFactLibrary).join(Fact).where(
            and_(
                UserFactLibrary.user_id == user_id,
                Fact.type == fact_type,
                cast(UserFactLibrary.saved_at, Date) == today_utc
            )
        )
        result = db.execute(saved_today_query)
        saved_today = result.scalar_one_or_none()
        
        if saved_today:
            # User has already read a tip today - return None
            return None
        
        # Get current pointer
        query = select(FactTODPointer).where(FactTODPointer.type == fact_type)
        result = db.execute(query)
        pointer = result.scalar_one_or_none()
        
        if not pointer or pointer.current_fact_id is None:
            return None
        
        # Return the current pointer fact
        return self.get_fact_by_id(db, fact_id=pointer.current_fact_id)

    def update_fact(self, db: Session, *, fact_id: int, obj_in: FactUpdate) -> Fact:
        """Update a fact"""
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Apply updates
        for field, value in update_data.items():
            if hasattr(fact, field):
                setattr(fact, field, value)

        db.commit()
        db.refresh(fact)
        return fact

    def delete_fact(self, db: Session, *, fact_id: int) -> Fact:
        """Delete a fact and handle pointer advancement if it's the current TOD"""
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")

        # Check if this fact is the current TOD for its type
        query = select(FactTODPointer).where(
            and_(
                FactTODPointer.type == fact.type,
                FactTODPointer.current_fact_id == fact_id
            )
        )
        result = db.execute(query)
        pointer = result.scalar_one_or_none()
        
        if pointer:
            # This fact is the current TOD, advance pointer before deleting
            self._advance_pointer(db, pointer=pointer, skip_fact_id=fact_id)

        # Delete the fact (cascade will handle user_fact_library entries)
        db.delete(fact)
        db.commit()
        return fact

    def bulk_create_facts(self, db: Session, *, facts_data: List[dict]) -> dict:
        """Bulk create facts from Excel upload with validation"""
        total_rows = len(facts_data)
        inserted = 0
        failed = 0
        errors = []
        
        valid_types = {ft.value for ft in FactType}
        
        for idx, row_data in enumerate(facts_data, start=2):  # Start at 2 (Excel row 1 is header)
            try:
                # Validate required fields
                if not row_data.get('title') or not row_data.get('description') or not row_data.get('type'):
                    errors.append({
                        "row": idx,
                        "reason": "Missing required field(s): title, description, or type"
                    })
                    failed += 1
                    continue
                
                # Validate type enum
                fact_type = row_data.get('type', '').strip().lower()
                if fact_type not in valid_types:
                    errors.append({
                        "row": idx,
                        "reason": f"Invalid type: '{row_data.get('type')}'. Must be: gut, nutrition, or sleep"
                    })
                    failed += 1
                    continue
                
                # Create fact
                fact = Fact(
                    title=row_data['title'].strip(),
                    description=row_data['description'].strip(),
                    type=FactType(fact_type)
                )
                db.add(fact)
                inserted += 1
                
            except Exception as e:
                errors.append({
                    "row": idx,
                    "reason": str(e)
                })
                failed += 1
        
        # Commit all valid inserts in single transaction
        if inserted > 0:
            db.commit()
            
            # Initialize pointers for any types that now have facts
            for fact_type in FactType:
                self._initialize_pointer_if_needed(db, fact_type=fact_type)
        
        return {
            "total_rows": total_rows,
            "inserted": inserted,
            "failed": failed,
            "errors": errors
        }

    def advance_tod_pointers(self, db: Session) -> dict:
        """Advance all TOD pointers (called by cron job)"""
        today_utc = datetime.utcnow().date()
        
        results = {}
        
        for fact_type in FactType:
            query = select(FactTODPointer).where(FactTODPointer.type == fact_type)
            result = db.execute(query)
            pointer = result.scalar_one_or_none()
            
            if not pointer:
                results[fact_type.value] = {"status": "skipped", "reason": "No pointer found"}
                continue
            
            # Idempotent guard: check if already advanced today (UTC)
            if pointer.last_updated_at:
                last_update_date = pointer.last_updated_at.date()
                if last_update_date >= today_utc:
                    results[fact_type.value] = {"status": "skipped", "reason": "Already advanced today"}
                    continue
            
            old_fact_id = pointer.current_fact_id
            self._advance_pointer(db, pointer=pointer)
            
            results[fact_type.value] = {
                "status": "advanced",
                "old_fact_id": old_fact_id,
                "new_fact_id": pointer.current_fact_id
            }
        
        db.commit()
        return results

    def _advance_pointer(self, db: Session, *, pointer: FactTODPointer, skip_fact_id: Optional[int] = None):
        """Advance pointer to next fact in queue"""
        # Get next fact with higher ID
        query = select(Fact).where(Fact.type == pointer.type)
        
        if pointer.current_fact_id:
            query = query.where(Fact.id > pointer.current_fact_id)
        
        if skip_fact_id:
            query = query.where(Fact.id != skip_fact_id)
        
        query = query.order_by(Fact.id.asc()).limit(1)
        result = db.execute(query)
        next_fact = result.scalar_one_or_none()
        
        if next_fact:
            # Found next fact
            pointer.current_fact_id = next_fact.id
        else:
            # No next fact, loop back to first fact
            query = select(Fact).where(Fact.type == pointer.type)
            if skip_fact_id:
                query = query.where(Fact.id != skip_fact_id)
            query = query.order_by(Fact.id.asc()).limit(1)
            result = db.execute(query)
            first_fact = result.scalar_one_or_none()
            
            if first_fact:
                pointer.current_fact_id = first_fact.id
            else:
                # No facts exist for this type
                pointer.current_fact_id = None
        
        pointer.last_updated_at = datetime.utcnow()

    def _initialize_pointer_if_needed(self, db: Session, *, fact_type: FactType):
        """Initialize pointer for a type if it doesn't exist or is null"""
        query = select(FactTODPointer).where(FactTODPointer.type == fact_type)
        result = db.execute(query)
        pointer = result.scalar_one_or_none()
        
        if not pointer:
            # Create pointer
            query = select(Fact).where(Fact.type == fact_type).order_by(Fact.id.asc()).limit(1)
            result = db.execute(query)
            first_fact = result.scalar_one_or_none()
            
            pointer = FactTODPointer(
                type=fact_type,
                current_fact_id=first_fact.id if first_fact else None
            )
            db.add(pointer)
            db.commit()
        elif pointer.current_fact_id is None:
            # Pointer exists but is null, set to first fact
            query = select(Fact).where(Fact.type == fact_type).order_by(Fact.id.asc()).limit(1)
            result = db.execute(query)
            first_fact = result.scalar_one_or_none()
            
            if first_fact:
                pointer.current_fact_id = first_fact.id
                db.commit()

    # User Fact Library methods
    def save_to_library(self, db: Session, *, user_id: int, fact_id: int) -> UserFactLibrary:
        """
        Save fact to user's library with current timestamp.
        Called when user clicks 'Read More'.
        The saved_at timestamp is used to check if user has read a tip today.
        """
        # Check if fact exists
        fact = self.get_fact_by_id(db, fact_id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")
        
        # Save to library (update timestamp even if already exists)
        query = select(UserFactLibrary).where(
            and_(
                UserFactLibrary.user_id == user_id,
                UserFactLibrary.fact_id == fact_id
            )
        )
        result = db.execute(query)
        existing = result.scalar_one_or_none()
        
        if not existing:
            # Create new entry
            library_entry = UserFactLibrary(
                user_id=user_id,
                fact_id=fact_id,
                saved_at=datetime.utcnow()
            )
            db.add(library_entry)
        else:
            # Update existing entry's timestamp to reflect current view
            existing.saved_at = datetime.utcnow()
            library_entry = existing
        
        db.commit()
        db.refresh(library_entry)
        return library_entry

    def get_user_library(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        fact_type: Optional[FactType] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserFactLibrary]:
        """Get user's fact library with optional type filter"""
        query = select(UserFactLibrary).where(
            UserFactLibrary.user_id == user_id
        ).options(
            joinedload(UserFactLibrary.fact)
        )
        
        if fact_type:
            query = query.join(Fact).where(Fact.type == fact_type)
        
        query = query.order_by(UserFactLibrary.saved_at.desc()).offset(skip).limit(limit)
        
        result = db.execute(query)
        return result.scalars().all()

    def count_user_library(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        fact_type: Optional[FactType] = None
    ) -> int:
        """Count facts in user's library"""
        query = select(func.count(UserFactLibrary.id)).where(
            UserFactLibrary.user_id == user_id
        )
        
        if fact_type:
            query = query.join(Fact).where(Fact.type == fact_type)
        
        result = db.execute(query)
        return result.scalar()


fact_crud = CRUDFact()
