from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.models.challenge import ChallengeType, ChallengeStatus, UserChallenge
from app.crud.challenge_crud import challenge_crud
from app.crud.reward_crud import reward_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.challenge_schema import (
    ChallengeCreate, ChallengeUpdate, ChallengeRead,
    UserChallengeCreate, UserChallengeRead, UserChallengeUpdate,
    ChallengeStatsResponse, RewardSummaryResponse
)


router = APIRouter(prefix="/challenges", tags=["Challenges"])

@router.post("/", response_model=APIResponse[ChallengeRead])
@standardize_response
def create_challenge(
    *,
    db: Session = Depends(get_db),
    challenge_in: ChallengeCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new challenge template (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create challenges")
    
    # Manual validation for reward time limits
    if challenge_in.reward_time_type == 'hour' and challenge_in.reward_time > 24:
        raise HTTPException(
            status_code=422, 
            detail="Reward time cannot be more than 24 hours. Use days instead."
        )
    
    challenge = challenge_crud.create_challenge(db=db, obj_in=challenge_in)
    return success_response(
        data=challenge,
        message="Challenge created successfully",
        status_code=201
    )


@router.get("/", response_model=APIResponse[List[dict]])
@standardize_response
def get_all_challenges(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get all challenges with flattened response and user participation status"""
    # Only admins can see inactive challenges
    if include_inactive and current_user.role.value != "admin":
        include_inactive = False
    
    # Get all challenges
    challenges = challenge_crud.get_all_challenges(db=db, skip=skip, limit=limit, include_inactive=include_inactive)
    
    # Get user's participation status for these challenges
    challenge_ids = [c.id for c in challenges]
    user_challenges = db.execute(
        select(UserChallenge).where(
            and_(UserChallenge.user_id == current_user.id, 
                 UserChallenge.challenge_id.in_(challenge_ids))
        )
    ).scalars().all()
    
    # Create a mapping of challenge_id -> user_challenge
    user_challenge_map = {uc.challenge_id: uc for uc in user_challenges}
    
    # Create flattened response structure
    flattened_data = []
    for challenge in challenges:
        user_challenge = user_challenge_map.get(challenge.id)
        
        flattened_item = {
            # Challenge basic info
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "type": challenge.type.value,
            "duration": challenge.duration,
            "duration_type": challenge.duration_type.value,
            "reward_time": challenge.reward_time,
            "reward_time_type": challenge.reward_time_type,
            "is_active": challenge.is_active,
            "created_at": challenge.created_at.isoformat(),
            "updated_at": challenge.updated_at.isoformat(),
            "duration_display_text": challenge.duration_display_text,
            "reward_display_text": challenge.reward_display_text,
            
            # User progress info (if user has joined)
            "user_challenge_id": user_challenge.id if user_challenge else None,
            "status": user_challenge.status.value if user_challenge else "pending",
            "current_progress": user_challenge.current_progress if user_challenge else 0,
            "progress_percentage": user_challenge.progress_percentage if user_challenge else 0.0,
            "progress_display_text": user_challenge.progress_display_text if user_challenge else f"0/{challenge.duration} {challenge.duration_type.value}{'s' if challenge.duration != 1 else ''}",
            "remaining_actions": user_challenge.remaining_actions if user_challenge else challenge.duration,
            "started_at": user_challenge.started_at.isoformat() if user_challenge else None,
            "completed_at": user_challenge.completed_at.isoformat() if user_challenge and user_challenge.completed_at else None,
            "last_progress_date": user_challenge.last_progress_date.isoformat() if user_challenge and user_challenge.last_progress_date else None,
            "last_progress_hour": user_challenge.last_progress_hour if user_challenge else None,
            "is_completed": user_challenge.is_completed if user_challenge else False,
            "is_user_active": user_challenge.is_active if user_challenge else False
        }
        flattened_data.append(flattened_item)
    
    return success_response(
        data=flattened_data,
        message="Challenges retrieved successfully"
    )


@router.get("/type/{challenge_type}", response_model=APIResponse[List[dict]])
@standardize_response
def get_challenges_by_type(
    challenge_type: ChallengeType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all active challenges by type with flattened response and user participation status"""
    # Get all active challenges of this type
    challenges = challenge_crud.get_challenges_by_type(db=db, challenge_type=challenge_type, skip=skip, limit=limit)
    
    # Get user's participation status for these challenges
    challenge_ids = [c.id for c in challenges]
    user_challenges = db.execute(
        select(UserChallenge).where(
            and_(UserChallenge.user_id == current_user.id, 
                 UserChallenge.challenge_id.in_(challenge_ids))
        )
    ).scalars().all()
    
    # Create a mapping of challenge_id -> user_challenge
    user_challenge_map = {uc.challenge_id: uc for uc in user_challenges}
    
    # Create flattened response structure
    flattened_data = []
    for challenge in challenges:
        user_challenge = user_challenge_map.get(challenge.id)
        
        flattened_item = {
            # Challenge basic info
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "type": challenge.type.value,
            "duration": challenge.duration,
            "duration_type": challenge.duration_type.value,
            "reward_time": challenge.reward_time,
            "reward_time_type": challenge.reward_time_type,
            "is_active": challenge.is_active,
            "created_at": challenge.created_at.isoformat(),
            "updated_at": challenge.updated_at.isoformat(),
            "duration_display_text": challenge.duration_display_text,
            "reward_display_text": challenge.reward_display_text,
            
            # User progress info (if user has joined)
            "user_challenge_id": user_challenge.id if user_challenge else None,
            "status": user_challenge.status.value if user_challenge else "pending",
            "current_progress": user_challenge.current_progress if user_challenge else 0,
            "progress_percentage": user_challenge.progress_percentage if user_challenge else 0.0,
            "progress_display_text": user_challenge.progress_display_text if user_challenge else f"0/{challenge.duration} {challenge.duration_type.value}{'s' if challenge.duration != 1 else ''}",
            "remaining_actions": user_challenge.remaining_actions if user_challenge else challenge.duration,
            "started_at": user_challenge.started_at.isoformat() if user_challenge else None,
            "completed_at": user_challenge.completed_at.isoformat() if user_challenge and user_challenge.completed_at else None,
            "last_progress_date": user_challenge.last_progress_date.isoformat() if user_challenge and user_challenge.last_progress_date else None,
            "last_progress_hour": user_challenge.last_progress_hour if user_challenge else None,
            "is_completed": user_challenge.is_completed if user_challenge else False,
            "is_user_active": user_challenge.is_active if user_challenge else False
        }
        flattened_data.append(flattened_item)
    
    return success_response(
        data=flattened_data,
        message=f"{challenge_type.value.title()} challenges retrieved successfully"
    )


@router.get("/my-challenges", response_model=APIResponse[List[dict]])
@standardize_response
def get_my_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[ChallengeStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get current user's challenges with flattened response"""
    user_challenges = challenge_crud.get_user_challenges(
        db=db, user_id=current_user.id, status=status, skip=skip, limit=limit
    )
    
    # Create flattened response structure
    flattened_data = []
    for uc in user_challenges:
        try:
            flattened_item = {
                # Challenge basic info (from challenge)
                "id": uc.challenge.id,
                "title": uc.challenge.title,
                "description": uc.challenge.description,
                "type": uc.challenge.type.value,
                "duration": uc.challenge.duration,
                "duration_type": uc.challenge.duration_type.value,
                "reward_time": uc.challenge.reward_time,
                "reward_time_type": uc.challenge.reward_time_type,
                "is_active": uc.challenge.is_active,
                "created_at": uc.challenge.created_at.isoformat(),
                "updated_at": uc.challenge.updated_at.isoformat(),
                "duration_display_text": uc.challenge.duration_display_text,
                "reward_display_text": uc.challenge.reward_display_text,
                
                # User progress info (from user_challenge)
                "user_challenge_id": uc.id,
                "status": uc.status.value,
                "current_progress": uc.current_progress,
                "progress_percentage": uc.progress_percentage,
                "progress_display_text": uc.progress_display_text,
                "remaining_actions": uc.remaining_actions,
                "started_at": uc.started_at.isoformat(),
                "completed_at": uc.completed_at.isoformat() if uc.completed_at else None,
                "last_progress_date": uc.last_progress_date.isoformat() if uc.last_progress_date else None,
                "last_progress_hour": uc.last_progress_hour,
                "is_completed": uc.is_completed,
                "is_user_active": uc.is_active
            }
            flattened_data.append(flattened_item)
        except Exception as e:
            print(f"Error flattening user challenge {uc.id}: {e}")
            continue
    
    return success_response(
        data=flattened_data,
        message="User challenges retrieved successfully"
    )


@router.get("/my-stats", response_model=APIResponse[ChallengeStatsResponse])
@standardize_response
def get_my_challenge_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get challenge statistics for current user"""
    stats = challenge_crud.get_user_challenge_stats(db=db, user_id=current_user.id)
    
    response_data = ChallengeStatsResponse(
        total_challenges=stats["total_challenges"],
        active_challenges=stats["active_challenges"],
        completed_challenges=stats["completed_challenges"],
        total_rewards_earned=stats["total_rewards_earned"]
    )
    
    return success_response(
        data=response_data,
        message="Challenge statistics retrieved successfully"
    )


@router.get("/my-rewards", response_model=APIResponse[RewardSummaryResponse])
@standardize_response
def get_my_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reward_summary = reward_crud.get_reward_summary(db=db, user_id=current_user.id)
    
    response_data = RewardSummaryResponse(
        total_active_rewards=reward_summary["active_rewards"],
        total_reward_time_hours=reward_summary["total_reward_time_hours"],
        total_reward_time_days=reward_summary["total_reward_time_days"],
        rewards=reward_summary["rewards"]
    )
    
    return success_response(
        data=response_data,
        message="Reward summary retrieved successfully"
    )


@router.get("/{challenge_id}", response_model=APIResponse[ChallengeRead])
@standardize_response
def get_challenge_by_id(
    challenge_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific challenge by ID"""
    challenge = challenge_crud.get_challenge_by_id(db=db, challenge_id=challenge_id)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    return success_response(
        data=challenge,
        message="Challenge retrieved successfully"
    )


@router.put("/{challenge_id}", response_model=APIResponse[ChallengeRead])
@standardize_response
def update_challenge(
    challenge_id: int,
    *,
    db: Session = Depends(get_db),
    challenge_in: ChallengeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a challenge (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update challenges")
    
    challenge = challenge_crud.update_challenge(db=db, challenge_id=challenge_id, obj_in=challenge_in)
    return success_response(
        data=challenge,
        message="Challenge updated successfully"
    )


@router.delete("/{challenge_id}", response_model=APIResponse[ChallengeRead])
@standardize_response
def delete_challenge(
    challenge_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a challenge (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete challenges")
    
    challenge = challenge_crud.delete_challenge(db=db, challenge_id=challenge_id)
    return success_response(
        data=challenge,
        message="Challenge deleted successfully"
    )


# User Challenge Participation
@router.post("/{challenge_id}/join", response_model=APIResponse[dict])
@standardize_response
def join_challenge(
    challenge_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a challenge (automatically starts) - returns flattened response"""
    user_challenge = challenge_crud.join_challenge(
        db=db, user_id=current_user.id, challenge_id=challenge_id
    )
    
    # Create flattened response structure
    flattened_data = {
        # Challenge basic info
        "id": user_challenge.challenge.id,
        "title": user_challenge.challenge.title,
        "description": user_challenge.challenge.description,
        "type": user_challenge.challenge.type.value,
        "duration": user_challenge.challenge.duration,
        "duration_type": user_challenge.challenge.duration_type.value,
        "reward_time": user_challenge.challenge.reward_time,
        "reward_time_type": user_challenge.challenge.reward_time_type,
        "is_active": user_challenge.challenge.is_active,
        "created_at": user_challenge.challenge.created_at.isoformat(),
        "updated_at": user_challenge.challenge.updated_at.isoformat(),
        "duration_display_text": user_challenge.challenge.duration_display_text,
        "reward_display_text": user_challenge.challenge.reward_display_text,
        
        # User progress info
        "user_challenge_id": user_challenge.id,
        "status": user_challenge.status.value,
        "current_progress": user_challenge.current_progress,
        "progress_percentage": user_challenge.progress_percentage,
        "progress_display_text": user_challenge.progress_display_text,
        "remaining_actions": user_challenge.remaining_actions,
        "started_at": user_challenge.started_at.isoformat(),
        "completed_at": user_challenge.completed_at.isoformat() if user_challenge.completed_at else None,
        "last_progress_date": user_challenge.last_progress_date.isoformat() if user_challenge.last_progress_date else None,
        "last_progress_hour": user_challenge.last_progress_hour,
        "is_completed": user_challenge.is_completed,
        "is_user_active": user_challenge.is_active
    }
    
    return success_response(
        data=flattened_data,
        message="Successfully joined challenge!",
        status_code=201
    )


@router.get("/user/{user_id}/challenges", response_model=APIResponse[List[UserChallengeRead]])
@standardize_response
def get_user_challenges(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[ChallengeStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get challenges for a specific user (Admin only or own challenges)"""
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own challenges")
    
    user_challenges = challenge_crud.get_user_challenges(
        db=db, user_id=user_id, status=status, skip=skip, limit=limit
    )
    return success_response(
        data=user_challenges,
        message="User challenges retrieved successfully"
    )


@router.put("/my-challenges/{user_challenge_id}/status", response_model=APIResponse[UserChallengeRead])
@standardize_response
def update_my_challenge_status(
    user_challenge_id: int,
    *,
    db: Session = Depends(get_db),
    challenge_update: UserChallengeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user's challenge status"""
    # Verify ownership
    user_challenge = challenge_crud.get_user_challenge_by_id(db=db, user_challenge_id=user_challenge_id)
    if not user_challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if user_challenge.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own challenges")
    
    updated_challenge = challenge_crud.update_user_challenge_status(
        db=db, user_challenge_id=user_challenge_id, obj_in=challenge_update
    )
    return success_response(
        data=updated_challenge,
        message="Challenge status updated successfully"
    )


@router.post("/my-challenges/{user_challenge_id}/update-progress", response_model=APIResponse[dict])
@standardize_response
def update_challenge_progress(
    user_challenge_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update challenge progress manually (action-based) - returns flattened response"""
    user_challenge = challenge_crud.get_user_challenge_by_id(db=db, user_challenge_id=user_challenge_id)
    if not user_challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if user_challenge.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own challenges")
    
    # Call the new action-based update_progress method
    result = user_challenge.update_progress()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Save changes to database
    db.commit()
    db.refresh(user_challenge)
    
    # Create flattened response structure
    flattened_data = {
        # Challenge basic info
        "id": user_challenge.challenge.id,
        "title": user_challenge.challenge.title,
        "description": user_challenge.challenge.description,
        "type": user_challenge.challenge.type.value,
        "duration": user_challenge.challenge.duration,
        "duration_type": user_challenge.challenge.duration_type.value,
        "reward_time": user_challenge.challenge.reward_time,
        "reward_time_type": user_challenge.challenge.reward_time_type,
        "is_active": user_challenge.challenge.is_active,
        "created_at": user_challenge.challenge.created_at.isoformat(),
        "updated_at": user_challenge.challenge.updated_at.isoformat(),
        "duration_display_text": user_challenge.challenge.duration_display_text,
        "reward_display_text": user_challenge.challenge.reward_display_text,
        
        # User progress info
        "user_challenge_id": user_challenge.id,
        "status": user_challenge.status.value,
        "current_progress": user_challenge.current_progress,
        "progress_percentage": user_challenge.progress_percentage,
        "progress_display_text": user_challenge.progress_display_text,
        "remaining_actions": user_challenge.remaining_actions,
        "started_at": user_challenge.started_at.isoformat(),
        "completed_at": user_challenge.completed_at.isoformat() if user_challenge.completed_at else None,
        "last_progress_date": user_challenge.last_progress_date.isoformat() if user_challenge.last_progress_date else None,
        "last_progress_hour": user_challenge.last_progress_hour,
        "is_completed": user_challenge.is_completed,
        "is_user_active": user_challenge.is_active,
        
        # Additional progress info
        "completed": result.get("completed", False),
        "message": result["message"]
    }
    
    return success_response(
        data=flattened_data,
        message=result["message"]
    )


@router.post("/admin/update-all-progress", response_model=APIResponse[dict])
@standardize_response
def update_all_challenges_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update progress for all active challenges (Admin only - for scheduler)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can trigger global progress updates")
    
    completed_count = challenge_crud.update_all_active_challenges_progress(db=db)
    
    return success_response(
        data={"completed_challenges": completed_count},
        message=f"Updated all active challenges. {completed_count} challenges completed."
    )
