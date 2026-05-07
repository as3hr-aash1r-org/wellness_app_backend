"""
User Level Service
Handles all user level upgrade logic and condition tracking
"""
from datetime import datetime, date
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.user import User, AppLevel
from app.models.user_level import UserLevelCondition, AppSession, ConditionKey


class LevelService:
    """Service for managing user levels and condition tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Session Tracking ====================
    
    def track_app_session(self, user_id: int, session_date: Optional[date] = None) -> None:
        """
        Track app session for a user on a specific date.
        Idempotent - safe to call multiple times per day.
        """
        if session_date is None:
            session_date = date.today()
        
        # Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING
        stmt = (
            pg_insert(AppSession)
            .values(
                user_id=user_id,
                session_date=session_date,
                created_at=datetime.utcnow()
            )
            .on_conflict_do_nothing(constraint='uq_user_session_date')
        )
        self.db.execute(stmt)
        self.db.flush()
        
        # Check if user now has 3+ distinct days
        self._check_app_opens_condition(user_id)
    
    def _check_app_opens_condition(self, user_id: int) -> None:
        """Check if user has opened app on 3+ distinct days"""
        count_query = select(func.count(AppSession.id)).where(
            AppSession.user_id == user_id
        )
        count = self.db.execute(count_query).scalar()
        
        if count >= 3:
            self.on_condition_met(
                user_id=user_id,
                condition_key=ConditionKey.app_opened_3_days,
                target_level=AppLevel.prospect
            )
    
    # ==================== Condition Tracking ====================
    
    def on_orientation_read(self, user_id: int) -> None:
        """User has read the Orientation document"""
        self.on_condition_met(
            user_id=user_id,
            condition_key=ConditionKey.orientation_read,
            target_level=AppLevel.prospect
        )
    
    def on_education_viewed(self, user_id: int) -> None:
        """User has viewed the Education section"""
        self.on_condition_met(
            user_id=user_id,
            condition_key=ConditionKey.education_viewed,
            target_level=AppLevel.prospect
        )
    
    def on_products_viewed(self, user_id: int) -> None:
        """User has viewed the Products section"""
        self.on_condition_met(
            user_id=user_id,
            condition_key=ConditionKey.products_viewed,
            target_level=AppLevel.prospect
        )
    
    def on_condition_met(
        self, 
        user_id: int, 
        condition_key: ConditionKey, 
        target_level: AppLevel
    ) -> None:
        """
        Record that a condition has been met.
        Idempotent - safe to call multiple times.
        """
        # Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING
        stmt = (
            pg_insert(UserLevelCondition)
            .values(
                user_id=user_id,
                condition_key=condition_key,
                target_level=target_level,
                met_at=datetime.utcnow()
            )
            .on_conflict_do_nothing(constraint='uq_user_condition')
        )
        result = self.db.execute(stmt)
        self.db.flush()
        
        # Only check upgrade if a new row was inserted
        if result.rowcount > 0 and target_level == AppLevel.prospect:
            self._try_upgrade_to_prospect(user_id)
    
    # ==================== Level Upgrades ====================
    
    def _try_upgrade_to_prospect(self, user_id: int) -> None:
        """
        Try to upgrade user to Prospect level.
        Early-exits if user is not currently new_joiner.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.app_level != AppLevel.new_joiner:
            return
        
        # Check all 3 conditions:
        # 1. Orientation read
        # 2. Education OR Products viewed
        # 3. App opened 3+ days
        
        conditions_query = select(UserLevelCondition.condition_key).where(
            and_(
                UserLevelCondition.user_id == user_id,
                UserLevelCondition.target_level == AppLevel.prospect
            )
        )
        met_conditions = set(self.db.execute(conditions_query).scalars().all())
        
        has_orientation = ConditionKey.orientation_read in met_conditions
        has_education_or_products = (
            ConditionKey.education_viewed in met_conditions or 
            ConditionKey.products_viewed in met_conditions
        )
        has_3_days = ConditionKey.app_opened_3_days in met_conditions
        
        if has_orientation and has_education_or_products and has_3_days:
            self._upgrade_user_level(user, AppLevel.prospect)
    
    def upgrade_to_dxn_new(self, user_id: int) -> None:
        """
        Upgrade user to DXN New level.
        Only upgrades if user is currently below DXN New.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        # Only upgrade if below DXN New
        level_order = [AppLevel.new_joiner, AppLevel.prospect, AppLevel.dxn_new, AppLevel.guide]
        current_index = level_order.index(user.app_level)
        dxn_new_index = level_order.index(AppLevel.dxn_new)
        
        if current_index < dxn_new_index:
            self._upgrade_user_level(user, AppLevel.dxn_new)
    
    def _upgrade_user_level(self, user: User, new_level: AppLevel) -> None:
        """Internal method to upgrade user level"""
        user.app_level = new_level
        user.level_upgraded_at = datetime.utcnow()
        self.db.flush()
    
    # ==================== Progress Tracking ====================
    
    def set_level(self, user_id: int, new_level: AppLevel) -> User:
        """
        Set user level directly (admin only).
        Allows any level change including downgrades.
        Raises ValueError if user not found.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if user.app_level != new_level:
            self._upgrade_user_level(user, new_level)
        
        return user
    
    def get_level_progress(self, user_id: int) -> Dict:
        """
        Get user's level progress and conditions met.
        Returns current level, met conditions, and progress toward next level.
        Raises ValueError if user not found.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        # Get met conditions
        conditions_query = select(UserLevelCondition).where(
            UserLevelCondition.user_id == user_id
        )
        conditions = self.db.execute(conditions_query).scalars().all()
        met_conditions = [c.condition_key.value for c in conditions]
        
        # Get app opens count
        app_opens_query = select(func.count(AppSession.id)).where(
            AppSession.user_id == user_id
        )
        app_opens_count = self.db.execute(app_opens_query).scalar() or 0
        
        # Determine next level and remaining conditions
        next_level = None
        conditions_remaining = []
        
        if user.app_level == AppLevel.new_joiner:
            next_level = "prospect"
            
            # Check Prospect conditions
            if ConditionKey.orientation_read.value not in met_conditions:
                conditions_remaining.append("orientation_read")
            
            if (ConditionKey.education_viewed.value not in met_conditions and 
                ConditionKey.products_viewed.value not in met_conditions):
                conditions_remaining.append("education_viewed OR products_viewed")
            
            if ConditionKey.app_opened_3_days.value not in met_conditions:
                conditions_remaining.append("app_opened_3_days")
        
        elif user.app_level == AppLevel.prospect:
            next_level = "dxn_new"
            if not (user.sponsor_code and user.distributor_code):
                conditions_remaining.append("save_sponsor_and_distributor_codes")
        
        elif user.app_level == AppLevel.dxn_new:
            next_level = "guide"
            conditions_remaining.append("admin_upgrade_only")
        
        return {
            "current_level": user.app_level.value,
            "level_upgraded_at": user.level_upgraded_at.isoformat() if user.level_upgraded_at else None,
            "next_level": next_level,
            "conditions_met": met_conditions,
            "conditions_remaining": conditions_remaining,
            "app_opens_count": app_opens_count,
            "codes_locked": bool(user.sponsor_code and user.distributor_code)
        }
