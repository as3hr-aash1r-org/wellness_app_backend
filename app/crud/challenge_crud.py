from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session, joinedload

from app.models.challenge import Challenge, UserChallenge, ChallengeType, ChallengeStatus
from app.models.user_rewards import UserReward, RewardType, RewardTimeType
from app.schemas.challenge_schema import ChallengeCreate, ChallengeUpdate, UserChallengeCreate, UserChallengeUpdate


class CRUDChallenge:
    # Challenge CRUD operations (Admin only)
    def create_challenge(self, db: Session, *, obj_in: ChallengeCreate) -> Challenge:
        """Create a new challenge template (Admin only)"""
        db_obj = Challenge(
            title=obj_in.title,
            description=obj_in.description,
            type=obj_in.type,
            duration=obj_in.duration,
            duration_type=obj_in.duration_type,
            reward_time=obj_in.reward_time,
            reward_time_type=obj_in.reward_time_type
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_challenge_by_id(self, db: Session, *, challenge_id: int) -> Optional[Challenge]:
        """Get a challenge by ID"""
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_challenges_by_type(self, db: Session, *, challenge_type: ChallengeType, skip: int = 0, limit: int = 100) -> List[Challenge]:
        """Get all active challenges by type"""
        query = select(Challenge).where(
            and_(Challenge.type == challenge_type, Challenge.is_active == True)
        ).offset(skip).limit(limit).order_by(Challenge.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_challenges_by_type(self, db: Session, *, challenge_type: ChallengeType) -> int:
        """Count challenges by type"""
        query = select(func.count(Challenge.id)).where(
            and_(Challenge.type == challenge_type, Challenge.is_active == True)
        )
        result = db.execute(query)
        return result.scalar()
    
    def get_challenges_by_type_with_user_status(self, db: Session, *, challenge_type: ChallengeType, user_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all active challenges by type with user participation status"""
        # Get all active challenges of this type
        challenges = self.get_challenges_by_type(db=db, challenge_type=challenge_type, skip=skip, limit=limit)
        
        # Get user's participation status for these challenges
        challenge_ids = [c.id for c in challenges]
        user_challenges = db.execute(
            select(UserChallenge).where(
                and_(UserChallenge.user_id == user_id, 
                     UserChallenge.challenge_id.in_(challenge_ids))
            )
        ).scalars().all()
        
        # Create a mapping of challenge_id -> user_status
        user_status_map = {uc.challenge_id: uc.status.value for uc in user_challenges}
        
        # Add status to each challenge
        result = []
        for challenge in challenges:
            challenge_dict = {
                "id": challenge.id,
                "title": challenge.title,
                "description": challenge.description,
                "type": challenge.type.value,
                "duration": challenge.duration,
                "duration_type": challenge.duration_type.value,
                "reward_time": challenge.reward_time,
                "reward_time_type": challenge.reward_time_type,
                "is_active": challenge.is_active,
                "created_at": challenge.created_at,
                "updated_at": challenge.updated_at,
                "duration_display_text": challenge.duration_display_text,
                "reward_display_text": challenge.reward_display_text,
                "status": user_status_map.get(challenge.id, "pending")  # Default to 'pending' if not joined
            }
            result.append(challenge_dict)
        
        return result

    def get_all_challenges(self, db: Session, *, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Challenge]:
        """Get all challenges with pagination"""
        query = select(Challenge)
        if not include_inactive:
            query = query.where(Challenge.is_active == True)
        query = query.offset(skip).limit(limit).order_by(Challenge.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_all_challenges(self, db: Session, *, include_inactive: bool = False) -> int:
        """Count all challenges"""
        query = select(func.count(Challenge.id))
        if not include_inactive:
            query = query.where(Challenge.is_active == True)
        result = db.execute(query)
        return result.scalar()
    
    def get_all_challenges_with_user_status(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[dict]:
        """Get all challenges with user participation status"""
        # Get all challenges
        challenges = self.get_all_challenges(db=db, skip=skip, limit=limit, include_inactive=include_inactive)
        
        # Get user's participation status for these challenges
        challenge_ids = [c.id for c in challenges]
        user_challenges = db.execute(
            select(UserChallenge).where(
                and_(UserChallenge.user_id == user_id, 
                     UserChallenge.challenge_id.in_(challenge_ids))
            )
        ).scalars().all()
        
        # Create a mapping of challenge_id -> user_status
        user_status_map = {uc.challenge_id: uc.status.value for uc in user_challenges}
        
        # Add status to each challenge
        result = []
        for challenge in challenges:
            challenge_dict = {
                "id": challenge.id,
                "title": challenge.title,
                "description": challenge.description,
                "type": challenge.type.value,
                "duration": challenge.duration,
                "duration_type": challenge.duration_type.value,
                "reward_time": challenge.reward_time,
                "reward_time_type": challenge.reward_time_type,
                "is_active": challenge.is_active,
                "created_at": challenge.created_at,
                "updated_at": challenge.updated_at,
                "duration_display_text": challenge.duration_display_text,
                "reward_display_text": challenge.reward_display_text,
                "status": user_status_map.get(challenge.id, "pending")  # Default to 'pending' if not joined
            }
            result.append(challenge_dict)
        
        return result

    def update_challenge(self, db: Session, *, challenge_id: int, obj_in: ChallengeUpdate) -> Challenge:
        """Update a challenge (Admin only)"""
        challenge = self.get_challenge_by_id(db, challenge_id=challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(challenge, field):
                setattr(challenge, field, value)

        db.commit()
        db.refresh(challenge)
        return challenge

    def delete_challenge(self, db: Session, *, challenge_id: int) -> Challenge:
        """Delete a challenge (Admin only)"""
        challenge = self.get_challenge_by_id(db, challenge_id=challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        # Check if any users are currently participating
        active_participations = db.execute(
            select(UserChallenge).where(
                and_(UserChallenge.challenge_id == challenge_id, 
                     UserChallenge.status == ChallengeStatus.active)
            )
        ).scalars().all()
        
        if active_participations:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete challenge with active participants. Deactivate it instead."
            )

        db.delete(challenge)
        db.commit()
        return challenge

    # User Challenge CRUD operations
    def join_challenge(self, db: Session, *, user_id: int, challenge_id: int) -> UserChallenge:
        """User joins a challenge (automatically starts)"""
        # Check if challenge exists and is active
        challenge = self.get_challenge_by_id(db, challenge_id=challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        if not challenge.is_active:
            raise HTTPException(status_code=400, detail="Challenge is not active")

        # Check if user is already participating in this challenge
        existing_participation = db.execute(
            select(UserChallenge).where(
                and_(UserChallenge.user_id == user_id, 
                     UserChallenge.challenge_id == challenge_id,
                     UserChallenge.status.in_([ChallengeStatus.active, ChallengeStatus.pending]))
            )
        ).scalar_one_or_none()
        
        if existing_participation:
            raise HTTPException(status_code=400, detail="You are already participating in this challenge")

        # Create user challenge participation
        user_challenge = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            status=ChallengeStatus.active  # Auto-start as per requirement
        )
        
        db.add(user_challenge)
        db.commit()
        db.refresh(user_challenge)
        return user_challenge

    def get_user_challenge_by_id(self, db: Session, *, user_challenge_id: int) -> Optional[UserChallenge]:
        """Get a user challenge by ID with challenge details"""
        query = select(UserChallenge).options(joinedload(UserChallenge.challenge)).where(
            UserChallenge.id == user_challenge_id
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_user_challenges(self, db: Session, *, user_id: int, status: Optional[ChallengeStatus] = None, skip: int = 0, limit: int = 100) -> List[UserChallenge]:
        """Get all challenges for a user"""
        query = select(UserChallenge).options(joinedload(UserChallenge.challenge)).where(
            UserChallenge.user_id == user_id
        )
        
        if status:
            query = query.where(UserChallenge.status == status)
        
        query = query.offset(skip).limit(limit).order_by(UserChallenge.created_at.desc())
        result = db.execute(query)
        return result.scalars().all()
    
    def count_user_challenges(self, db: Session, *, user_id: int, status: Optional[ChallengeStatus] = None) -> int:
        """Count user challenges"""
        query = select(func.count(UserChallenge.id)).where(UserChallenge.user_id == user_id)
        if status:
            query = query.where(UserChallenge.status == status)
        result = db.execute(query)
        return result.scalar()

    def update_user_challenge_status(self, db: Session, *, user_challenge_id: int, obj_in: UserChallengeUpdate) -> UserChallenge:
        """Update user challenge status"""
        user_challenge = self.get_user_challenge_by_id(db, user_challenge_id=user_challenge_id)
        if not user_challenge:
            raise HTTPException(status_code=404, detail="User challenge not found")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user_challenge, field):
                setattr(user_challenge, field, value)

        db.commit()
        db.refresh(user_challenge)
        return user_challenge

    def update_challenge_progress(self, db: Session, *, user_challenge_id: int) -> UserChallenge:
        """Update challenge progress and auto-complete if needed"""
        user_challenge = self.get_user_challenge_by_id(db, user_challenge_id=user_challenge_id)
        if not user_challenge:
            raise HTTPException(status_code=404, detail="User challenge not found")

        # Update progress using the model method
        user_challenge.update_progress()
        
        # If challenge is completed, create reward
        if user_challenge.status == ChallengeStatus.completed and not user_challenge.completed_at:
            self.create_challenge_reward(db, user_challenge)

        db.commit()
        db.refresh(user_challenge)
        return user_challenge

    def update_all_active_challenges_progress(self, db: Session):
        """Update progress for all active challenges (can be called by a scheduler)"""
        active_challenges = db.execute(
            select(UserChallenge).options(joinedload(UserChallenge.challenge)).where(
                UserChallenge.status == ChallengeStatus.active
            )
        ).scalars().all()
        
        completed_challenges = []
        for user_challenge in active_challenges:
            user_challenge.update_progress()
            if user_challenge.status == ChallengeStatus.completed:
                self.create_challenge_reward(db, user_challenge)
                completed_challenges.append(user_challenge)
        
        if completed_challenges:
            db.commit()
        
        return len(completed_challenges)

    def create_challenge_reward(self, db: Session, user_challenge: UserChallenge):
        """Create reward for completed challenge"""
        challenge = user_challenge.challenge
        
        # Determine reward time type
        reward_time_type = RewardTimeType.hour if challenge.reward_time_type == 'hour' else RewardTimeType.day
        print(f"HERERER 2", challenge.reward_time)
        reward = UserReward(
            user_id=user_challenge.user_id,
            reward_type=RewardType.referral_bonus,
            description=f"Challenge completed: {challenge.title}",
            reward_time=challenge.reward_time,
            reward_time_type=reward_time_type,
            user_challenge_id=user_challenge.id
        )
        print(f"USER ID IN REWARD: ",user_challenge.user_id)
        db.add(reward)
        db.commit()
        db.refresh(reward)
        return reward

    def get_user_challenge_stats(self, db: Session, *, user_id: int) -> dict:
        """Get challenge statistics for a user"""
        total_challenges = db.execute(
            select(func.count(UserChallenge.id)).where(UserChallenge.user_id == user_id)
        ).scalar()
        
        active_challenges = db.execute(
            select(func.count(UserChallenge.id)).where(
                and_(UserChallenge.user_id == user_id, UserChallenge.status == ChallengeStatus.active)
            )
        ).scalar()
        
        completed_challenges = db.execute(
            select(func.count(UserChallenge.id)).where(
                and_(UserChallenge.user_id == user_id, UserChallenge.status == ChallengeStatus.completed)
            )
        ).scalar()
        
        # Count challenge rewards
        total_rewards_earned = db.execute(
            select(func.count(UserReward.id)).where(
                and_(UserReward.user_id == user_id, UserReward.reward_type == RewardType.challenge_reward)
            )
        ).scalar()
        
        return {
            "total_challenges": total_challenges or 0,
            "active_challenges": active_challenges or 0,
            "completed_challenges": completed_challenges or 0,
            "total_rewards_earned": total_rewards_earned or 0
        }


challenge_crud = CRUDChallenge()
