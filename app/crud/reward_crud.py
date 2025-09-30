from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user_rewards import UserReward, RewardType, RewardStatus
from app.models.referrals import Referrals


class CRUDReward:
    """CRUD operations for user rewards system"""
    
    def create_referral_reward(self, db: Session, *, user_id: int, referral_id: int, reward_type: RewardType = RewardType.referral_bonus) -> UserReward:
        """Create a referral reward for a user"""
        description = "30-day discount for successful referral" if reward_type == RewardType.referral_bonus else "Welcome bonus - 30-day discount"
        
        reward = UserReward(
            user_id=user_id,
            reward_type=reward_type,
            description=description,
            discount_days=30,
            referral_id=referral_id if reward_type == RewardType.referral_bonus else None,
            status=RewardStatus.active,
            created_at=datetime.utcnow()
        )
        
        db.add(reward)
        db.commit()
        db.refresh(reward)
        return reward
    
    def create_signup_bonus(self, db: Session, *, user_id: int) -> UserReward:
        """Create a signup bonus reward for new user who used referral code"""
        reward = UserReward(
            user_id=user_id,
            reward_type=RewardType.signup_bonus,
            description="30-day discount for joining with referral code",
            discount_days=30,
            status=RewardStatus.active,
            created_at=datetime.utcnow()
        )
        
        db.add(reward)
        db.commit()
        db.refresh(reward)
        return reward
    
    def get_user_rewards(self, db: Session, *, user_id: int, active_only: bool = False):
        """Get all rewards for a user"""
        query = select(UserReward).where(UserReward.user_id == user_id)
        
        if active_only:
            query = query.where(UserReward.status == RewardStatus.active)
        
        result = db.execute(query)
        return result.scalars().all()
    
    def get_active_rewards(self, db: Session, *, user_id: int):
        """Get only active, non-expired rewards for a user"""
        rewards = self.get_user_rewards(db, user_id=user_id, active_only=True)
        
        # Filter out expired rewards and update their status
        active_rewards = []
        for reward in rewards:
            if reward.is_expired:
                reward.mark_as_expired()
                db.commit()
            elif reward.is_active:
                active_rewards.append(reward)
        
        return active_rewards
    
    def use_reward(self, db: Session, *, reward_id: int, user_id: int) -> UserReward:
        """Mark a reward as used"""
        query = select(UserReward).where(
            UserReward.id == reward_id,
            UserReward.user_id == user_id,
            UserReward.status == RewardStatus.active
        )
        result = db.execute(query)
        reward = result.scalar_one_or_none()
        
        if not reward:
            raise HTTPException(status_code=404, detail="Reward not found or already used")
        
        if reward.is_expired:
            reward.mark_as_expired()
            db.commit()
            raise HTTPException(status_code=400, detail="Reward has expired")
        
        reward.mark_as_used()
        db.commit()
        db.refresh(reward)
        return reward
    
    def get_reward_summary(self, db: Session, *, user_id: int) -> dict:
        """Get a summary of user's rewards"""
        all_rewards = self.get_user_rewards(db, user_id=user_id)
        active_rewards = self.get_active_rewards(db, user_id=user_id)
        
        total_discount_days = sum(reward.discount_days for reward in active_rewards)
        
        return {
            "total_rewards": len(all_rewards),
            "active_rewards": len(active_rewards),
            "total_discount_days_available": total_discount_days,
            "rewards": active_rewards
        }
    
    def process_referral_rewards(self, db: Session, *, referrer_id: int, referred_user_id: int, referral_id: int) -> dict:
        """Process rewards for both referrer and referred user"""
        try:
            # Create reward for referrer (person who referred)
            referrer_reward = self.create_referral_reward(
                db=db,
                user_id=referrer_id,
                referral_id=referral_id,
                reward_type=RewardType.referral_bonus
            )
            
            # Create signup bonus for new user (person who was referred)
            referred_reward = self.create_signup_bonus(
                db=db,
                user_id=referred_user_id
            )
            
            return {
                "success": True,
                "referrer_reward": referrer_reward,
                "referred_reward": referred_reward,
                "message": "Rewards created successfully for both users"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error creating rewards: {str(e)}"
            }


reward_crud = CRUDReward()
