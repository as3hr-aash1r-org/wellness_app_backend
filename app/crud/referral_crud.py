from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User
from app.models.referrals import Referrals
from app.utils.referral_code_generator import validate_referral_code


class CRUDReferral:
    """CRUD operations for referral system"""
    
    def get_user_by_referral_code(self, db: Session, *, referral_code: str) -> User:
        """Find user by their referral code"""
        if not validate_referral_code(referral_code):
            return None
            
        query = select(User).where(User.referral_code == referral_code)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def create_referral_relationship(self, db: Session, *, referral_code: str, referrer_user_id: int, referred_user_id: int) -> Referrals:
        """Create a referral relationship between users"""
        # Check if relationship already exists
        existing_query = select(Referrals).where(
            Referrals.referred_user_id == referred_user_id
        )
        existing = db.execute(existing_query).scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="User has already been referred")
        
        # Create new referral relationship
        referral_obj = Referrals(
            referral_code=referral_code,
            referrer_user_id=referrer_user_id,
            referred_user_id=referred_user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(referral_obj)
        db.commit()
        db.refresh(referral_obj)
        return referral_obj
    
    def get_user_referrals(self, db: Session, *, user_id: int):
        """Get all users referred by a specific user"""
        query = select(Referrals).where(Referrals.referrer_user_id == user_id)
        result = db.execute(query)
        return result.scalars().all()
    
    def get_referral_stats(self, db: Session, *, user_id: int) -> dict:
        """Get referral statistics for a user"""
        referrals = self.get_user_referrals(db, user_id=user_id)
        
        total_referrals = len(referrals)
        recent_referrals = len([r for r in referrals if r.created_at >= datetime.utcnow() - timedelta(days=30)])
        
        return {
            "total_referrals": total_referrals,
            "recent_referrals": recent_referrals,
            "referral_details": referrals
        }
    
    def validate_and_process_referral(self, db: Session, *, referral_code: str, new_user_id: int) -> dict:
        """
        Validate referral code and process the referral
        Returns dict with referrer info and success status
        """
        if not referral_code:
            return {"success": False, "message": "No referral code provided"}
        
        # Validate format
        if not validate_referral_code(referral_code):
            return {"success": False, "message": "Invalid referral code format"}
        
        # Find referrer user
        referrer = self.get_user_by_referral_code(db, referral_code=referral_code)
        if not referrer:
            return {"success": False, "message": "Referral code not found"}
        
        # Check if user is trying to refer themselves
        if referrer.id == new_user_id:
            return {"success": False, "message": "Cannot use your own referral code"}
        
        try:
            # Create referral relationship
            referral_relationship = self.create_referral_relationship(
                db=db,
                referral_code=referral_code,
                referrer_user_id=referrer.id,
                referred_user_id=new_user_id
            )
            
            return {
                "success": True,
                "message": "Referral processed successfully",
                "referrer": referrer,
                "referral_relationship": referral_relationship
            }
            
        except HTTPException as e:
            return {"success": False, "message": str(e.detail)}
        except Exception as e:
            return {"success": False, "message": f"Error processing referral: {str(e)}"}


referral_crud = CRUDReferral()
