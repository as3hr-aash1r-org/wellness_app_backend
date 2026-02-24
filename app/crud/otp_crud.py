import random
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app.models.otp import OTP


class CRUDOTP:
    
    @staticmethod
    def generate_otp_code() -> str:
        """Generate a 6-digit OTP code"""
        return str(random.randint(100000, 999999))
    
    def create_otp(self, db: Session, phone_number: str) -> OTP:
        """Create a new OTP record"""
        otp_code = self.generate_otp_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Invalidate any existing OTPs for this phone number
        self.invalidate_existing_otps(db, phone_number)
        
        db_obj = OTP(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at,
            attempts=0,
            is_verified=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def invalidate_existing_otps(self, db: Session, phone_number: str):
        """Mark all existing OTPs for a phone number as verified (invalidate them)"""
        query = select(OTP).where(
            and_(
                OTP.phone_number == phone_number,
                OTP.is_verified == False
            )
        )
        result = db.execute(query)
        otps = result.scalars().all()
        
        for otp in otps:
            otp.is_verified = True
        
        db.commit()
    
    def get_valid_otp(self, db: Session, phone_number: str) -> OTP:
        """Get the most recent valid OTP for a phone number"""
        query = select(OTP).where(
            and_(
                OTP.phone_number == phone_number,
                OTP.is_verified == False,
                OTP.expires_at > datetime.utcnow()
            )
        ).order_by(OTP.created_at.desc())
        
        result = db.execute(query)
        return result.scalars().first()
    
    def verify_otp(self, db: Session, phone_number: str, otp_code: str) -> dict:
        """
        Verify OTP code
        
        Returns:
            dict with success status and message
        """
        otp_record = self.get_valid_otp(db, phone_number)
        
        if not otp_record:
            return {
                "success": False,
                "message": "OTP expired or not found. Please request a new one."
            }
        
        # Check max attempts
        if otp_record.attempts >= 3:
            otp_record.is_verified = True  # Invalidate after max attempts
            db.commit()
            return {
                "success": False,
                "message": "Maximum verification attempts exceeded. Please request a new OTP."
            }
        
        # Increment attempts
        otp_record.attempts += 1
        db.commit()
        
        # Verify OTP code
        if otp_record.otp_code != otp_code:
            return {
                "success": False,
                "message": f"Invalid OTP code. {3 - otp_record.attempts} attempts remaining."
            }
        
        # Mark as verified
        otp_record.is_verified = True
        db.commit()
        
        return {
            "success": True,
            "message": "OTP verified successfully"
        }
    
    def can_request_otp(self, db: Session, phone_number: str) -> dict:
        """
        Check if user can request a new OTP (rate limiting)
        
        Returns:
            dict with can_request status and message
        """
        # Get the most recent OTP (verified or not)
        query = select(OTP).where(
            OTP.phone_number == phone_number
        ).order_by(OTP.created_at.desc())
        
        result = db.execute(query)
        last_otp = result.scalars().first()
        
        if not last_otp:
            return {"can_request": True}
        
        # Allow new OTP if last one was created more than 1 minute ago
        time_since_last = datetime.utcnow() - last_otp.created_at
        if time_since_last.total_seconds() < 60:
            wait_time = 60 - int(time_since_last.total_seconds())
            return {
                "can_request": False,
                "message": f"Please wait {wait_time} seconds before requesting a new OTP."
            }
        
        return {"can_request": True}


otp_crud = CRUDOTP()
