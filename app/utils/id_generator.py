from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User


class UserIDGenerator:
    """
    Generates unique incremental IDs for users
    - g_id: Genes ID (all users) - 5 digits starting from 00001
    - d_id: Department/Official ID (official users) - 5 digits starting from 00001
    - i_id: Influencer ID (influencer users) - 5 digits starting from 00001
    """
    
    @staticmethod
    def _format_id(number: int) -> str:
        """Format number as 5-digit string with leading zeros"""
        return f"{number:05d}"
    
    @classmethod
    def generate_g_id(cls, db: Session) -> str:
        """
        Generate next Genes ID (g_id) for any user
        Returns: 5-digit string like "00001", "00002", etc.
        """
        # Get the latest g_id from database
        query = select(User.g_id).where(
            User.g_id.isnot(None)
        ).order_by(User.g_id.desc()).limit(1)
        
        result = db.execute(query)
        latest_g_id = result.scalar_one_or_none()
        
        if not latest_g_id:
            # First g_id
            return cls._format_id(1)
        
        try:
            # Extract number and increment
            current_number = int(latest_g_id)
            new_number = current_number + 1
            new_g_id = cls._format_id(new_number)
            
            # Verify uniqueness (safety check)
            existing_query = select(User.id).where(User.g_id == new_g_id)
            existing = db.execute(existing_query).scalar_one_or_none()
            
            if existing:
                # Recursively try next number if collision occurs
                # This shouldn't happen but is a safety measure
                return cls._format_id(new_number + 1)
            
            return new_g_id
            
        except ValueError:
            # If parsing fails, start fresh
            return cls._format_id(1)
    
    @classmethod
    def generate_d_id(cls, db: Session) -> str:
        """
        Generate next Department/Official ID (d_id) for official users
        Returns: 5-digit string like "00001", "00002", etc.
        """
        # Get the latest d_id from database
        query = select(User.d_id).where(
            User.d_id.isnot(None)
        ).order_by(User.d_id.desc()).limit(1)
        
        result = db.execute(query)
        latest_d_id = result.scalar_one_or_none()
        
        if not latest_d_id:
            # First d_id
            return cls._format_id(1)
        
        try:
            # Extract number and increment
            current_number = int(latest_d_id)
            new_number = current_number + 1
            new_d_id = cls._format_id(new_number)
            
            # Verify uniqueness (safety check)
            existing_query = select(User.id).where(User.d_id == new_d_id)
            existing = db.execute(existing_query).scalar_one_or_none()
            
            if existing:
                # Recursively try next number if collision occurs
                return cls._format_id(new_number + 1)
            
            return new_d_id
            
        except ValueError:
            # If parsing fails, start fresh
            return cls._format_id(1)
    
    @classmethod
    def generate_i_id(cls, db: Session) -> str:
        """
        Generate next Influencer ID (i_id) for influencer users
        Returns: 5-digit string like "00001", "00002", etc.
        """
        # Get the latest i_id from database
        query = select(User.i_id).where(
            User.i_id.isnot(None)
        ).order_by(User.i_id.desc()).limit(1)
        
        result = db.execute(query)
        latest_i_id = result.scalar_one_or_none()
        
        if not latest_i_id:
            # First i_id
            return cls._format_id(1)
        
        try:
            # Extract number and increment
            current_number = int(latest_i_id)
            new_number = current_number + 1
            new_i_id = cls._format_id(new_number)
            
            # Verify uniqueness (safety check)
            existing_query = select(User.id).where(User.i_id == new_i_id)
            existing = db.execute(existing_query).scalar_one_or_none()
            
            if existing:
                # Recursively try next number if collision occurs
                return cls._format_id(new_number + 1)
            
            return new_i_id
            
        except ValueError:
            # If parsing fails, start fresh
            return cls._format_id(1)


def generate_user_ids(db: Session, role: str) -> dict:
    """
    Generate appropriate IDs based on user role
    
    Args:
        db: Database session
        role: User role (official, influencer, user, etc.)
    
    Returns:
        dict with g_id and role-specific IDs
    """
    ids = {
        "g_id": UserIDGenerator.generate_g_id(db),
        "d_id": None,
        "i_id": None
    }
    
    # Generate role-specific IDs
    if role == "official":
        ids["d_id"] = UserIDGenerator.generate_d_id(db)
    elif role == "influencer":
        ids["i_id"] = UserIDGenerator.generate_i_id(db)
    
    return ids
