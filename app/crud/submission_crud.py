from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List

from app.models.submission import Submission, SubmissionStatus
from app.schemas.submission_schema import SubmissionCreate, SubmissionUpdate


class CRUDSubmission:
    def create(self, db: Session, *, obj_in: SubmissionCreate, influencer_id: int) -> Submission:
        media_data = [item.model_dump() for item in obj_in.media]
        
        db_obj = Submission(
            influencer_id=influencer_id,
            caption=obj_in.caption,
            tags=obj_in.tags,
            media=media_data,
            status=SubmissionStatus.pending,
            edited_by_admin=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, *, submission_id: int) -> Optional[Submission]:
        query = select(Submission).where(Submission.id == submission_id)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_influencer(
        self, 
        db: Session, 
        *, 
        influencer_id: int,
        status: Optional[SubmissionStatus] = None,
        from_date: Optional[datetime] = None
    ) -> List[Submission]:
        query = select(Submission).where(Submission.influencer_id == influencer_id)
        
        if status:
            query = query.where(Submission.status == status)
        if from_date:
            query = query.where(Submission.created_at >= from_date)
        
        query = query.order_by(Submission.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def get_all(
        self,
        db: Session,
        *,
        status: Optional[SubmissionStatus] = None,
        influencer_id: Optional[int] = None,
        from_date: Optional[datetime] = None
    ) -> List[Submission]:
        query = select(Submission)
        
        if status:
            query = query.where(Submission.status == status)
        if influencer_id:
            query = query.where(Submission.influencer_id == influencer_id)
        if from_date:
            query = query.where(Submission.created_at >= from_date)
        
        query = query.order_by(Submission.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def delete(self, db: Session, *, submission_id: int, influencer_id: int) -> Submission:
        submission = self.get_by_id(db, submission_id=submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.influencer_id != influencer_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this submission")
        
        if submission.status != SubmissionStatus.pending:
            raise HTTPException(
                status_code=400, 
                detail="Can only delete pending submissions"
            )
        
        db.delete(submission)
        db.commit()
        return submission
    
    def approve(self, db: Session, *, submission_id: int) -> Submission:
        submission = self.get_by_id(db, submission_id=submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission.status = SubmissionStatus.approved
        db.commit()
        db.refresh(submission)
        return submission
    
    def reject(self, db: Session, *, submission_id: int, feedback: str) -> Submission:
        submission = self.get_by_id(db, submission_id=submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission.status = SubmissionStatus.rejected
        submission.admin_feedback = feedback
        db.commit()
        db.refresh(submission)
        return submission
    
    def edit(self, db: Session, *, submission_id: int, obj_in: SubmissionUpdate) -> Submission:
        submission = self.get_by_id(db, submission_id=submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if 'media' in update_data and update_data['media']:
            update_data['media'] = [item.model_dump() for item in obj_in.media]
        
        for field, value in update_data.items():
            setattr(submission, field, value)
        
        submission.edited_by_admin = True
        db.commit()
        db.refresh(submission)
        return submission


submission_crud = CRUDSubmission()
