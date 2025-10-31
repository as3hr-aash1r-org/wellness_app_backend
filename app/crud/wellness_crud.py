from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from fastapi import HTTPException
from typing import List, Optional

from app.models.wellness import Wellness, WellnessType
from app.schemas.wellness_schema import WellnessCreate, WellnessUpdate


class CRUDWellness:
    def create_wellness(self, db: Session, *, obj_in: WellnessCreate) -> Wellness:
        """Create a new wellness activity (Admin only)"""
        db_obj = Wellness(
            title=obj_in.title,
            type=obj_in.type,
            steps=obj_in.steps,
            duration=obj_in.duration,
            benefits=obj_in.benefits
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_wellness_by_id(self, db: Session, *, wellness_id: int) -> Optional[Wellness]:
        """Get wellness activity by ID"""
        query = select(Wellness).where(Wellness.id == wellness_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_wellness_by_type(self, db: Session, *, wellness_type: WellnessType, skip: int = 0, limit: int = 100) -> List[Wellness]:
        """Get all wellness activities by type"""
        query = select(Wellness).where(
            Wellness.type == wellness_type
        ).offset(skip).limit(limit).order_by(Wellness.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_wellness_by_type(self, db: Session, *, wellness_type: WellnessType) -> int:
        """Count wellness activities by type"""
        query = select(func.count(Wellness.id)).where(Wellness.type == wellness_type)
        result = db.execute(query)
        return result.scalar()

    def get_all_wellness(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Wellness]:
        """Get all wellness activities with pagination"""
        query = select(Wellness).offset(skip).limit(limit).order_by(Wellness.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_all_wellness(self, db: Session) -> int:
        """Count all wellness activities"""
        query = select(func.count(Wellness.id))
        result = db.execute(query)
        return result.scalar()

    def update_wellness(self, db: Session, *, wellness_id: int, obj_in: WellnessUpdate) -> Wellness:
        """Update a wellness activity (Admin only)"""
        wellness = self.get_wellness_by_id(db, wellness_id=wellness_id)
        if not wellness:
            raise HTTPException(status_code=404, detail="Wellness activity not found")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(wellness, field, value)

        db.commit()
        db.refresh(wellness)
        return wellness

    def delete_wellness(self, db: Session, *, wellness_id: int) -> Wellness:
        """Delete a wellness activity (Admin only)"""
        wellness = self.get_wellness_by_id(db, wellness_id=wellness_id)
        if not wellness:
            raise HTTPException(status_code=404, detail="Wellness activity not found")

        db.delete(wellness)
        db.commit()
        return wellness

    def get_wellness_stats(self, db: Session) -> dict:
        """Get wellness statistics by type"""
        # Count total wellness activities
        total_query = select(func.count(Wellness.id))
        total_result = db.execute(total_query)
        total_wellness = total_result.scalar()

        # Count by type
        exercise_query = select(func.count(Wellness.id)).where(Wellness.type == WellnessType.exercise)
        exercise_result = db.execute(exercise_query)
        exercise_count = exercise_result.scalar()

        therapy_query = select(func.count(Wellness.id)).where(Wellness.type == WellnessType.therapy)
        therapy_result = db.execute(therapy_query)
        therapy_count = therapy_result.scalar()

        stress_query = select(func.count(Wellness.id)).where(Wellness.type == WellnessType.stress)
        stress_result = db.execute(stress_query)
        stress_count = stress_result.scalar()

        return {
            "total_wellness": total_wellness,
            "exercise_count": exercise_count,
            "therapy_count": therapy_count,
            "stress_count": stress_count
        }

    def search_wellness(self, db: Session, *, query: str, wellness_type: Optional[WellnessType] = None, skip: int = 0, limit: int = 100) -> List[Wellness]:
        """Search wellness activities by title or benefits"""
        search_query = select(Wellness).where(
            Wellness.title.ilike(f"%{query}%") | 
            Wellness.benefits.ilike(f"%{query}%")
        )
        
        if wellness_type:
            search_query = search_query.where(Wellness.type == wellness_type)
            
        search_query = search_query.offset(skip).limit(limit).order_by(Wellness.created_at.desc())
        result = db.execute(search_query)
        return result.scalars().all()
    
    def count_search_wellness(self, db: Session, *, query: str, wellness_type: Optional[WellnessType] = None) -> int:
        """Count search results for wellness activities"""
        search_query = select(func.count(Wellness.id)).where(
            Wellness.title.ilike(f"%{query}%") | 
            Wellness.benefits.ilike(f"%{query}%")
        )
        
        if wellness_type:
            search_query = search_query.where(Wellness.type == wellness_type)
            
        result = db.execute(search_query)
        return result.scalar()


# Create a global instance
wellness_crud = CRUDWellness()
