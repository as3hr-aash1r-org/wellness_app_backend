from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models.user_rewards import UserReward, RewardType, RewardStatus, RewardTimeType
from app.models.referrals import Referrals


class CRUDReward:
    """CRUD operations for user rewards system"""
    
    def create_referral_reward(self, db: Session, *, user_id: int, referral_id: int, reward_time: int = 30, reward_time_type: RewardTimeType = RewardTimeType.day, reward_type: RewardType = RewardType.referral_bonus) -> UserReward:
        """Create a referral reward for a user with flexible time"""
        description = f"{reward_time}-{reward_time_type.value} discount for successful referral" if reward_type == RewardType.referral_bonus else f"Welcome bonus - {reward_time}-{reward_time_type.value} discount"
        
        reward = UserReward(
            user_id=user_id,
            reward_type=reward_type,
            description=description,
            reward_time=reward_time,
            reward_time_type=reward_time_type,
            referral_id=referral_id if reward_type == RewardType.referral_bonus else None,
            status=RewardStatus.active,
            created_at=datetime.utcnow()
        )
        
        db.add(reward)
        db.commit()
        db.refresh(reward)
        return reward
    
    def create_signup_bonus(self, db: Session, *, user_id: int, reward_time: int = 30, reward_time_type: RewardTimeType = RewardTimeType.day) -> UserReward:
        """Create a signup bonus reward for new user who used referral code"""
        reward = UserReward(
            user_id=user_id,
            reward_type=RewardType.signup_bonus,
            description=f"{reward_time}-{reward_time_type.value} discount for joining with referral code",
            reward_time=reward_time,
            reward_time_type=reward_time_type,
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
        """Get a summary of user's rewards with flexible time units"""
        all_rewards = self.get_user_rewards(db, user_id=user_id)
        active_rewards = self.get_active_rewards(db, user_id=user_id)

        # Calculate total time by type
        total_hours = sum(reward.reward_time for reward in active_rewards 
                         if reward.reward_time_type == RewardTimeType.hour and reward.reward_time is not None)
        total_days = sum(reward.reward_time for reward in active_rewards 
                        if reward.reward_time_type == RewardTimeType.day and reward.reward_time is not None)
        
        # Format rewards for display
        formatted_rewards = []
        for reward in active_rewards:
            try:
                formatted_rewards.append({
                    "id": reward.id,
                    "description": reward.description or "",
                    "reward_display_text": reward.reward_display_text if hasattr(reward, 'reward_display_text') else f"{reward.reward_time or 0} {reward.reward_time_type.value if reward.reward_time_type else 'days'}",
                    "expires_at": reward.expires_at.isoformat() if reward.expires_at else None,
                    "reward_type": reward.reward_type.value if reward.reward_type else "unknown",
                    "created_at": reward.created_at.isoformat() if reward.created_at else None
                })
            except Exception as e:
                # Skip problematic rewards and log the error
                print(f"Error formatting reward {reward.id}: {str(e)}")
                continue
        
        return {
            "total_rewards": len(all_rewards),
            "active_rewards": len(active_rewards),
            "total_reward_time_hours": total_hours,
            "total_reward_time_days": total_days,
            "rewards": formatted_rewards
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
