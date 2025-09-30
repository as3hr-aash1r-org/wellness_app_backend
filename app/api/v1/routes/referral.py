from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.crud.referral_crud import referral_crud
from app.crud.reward_crud import reward_crud
from app.schemas.api_response import success_response, APIResponse
from pydantic import BaseModel


router = APIRouter(prefix="/referrals", tags=["Referrals"])


class ReferralStatsResponse(BaseModel):
    total_referrals: int
    recent_referrals: int
    user_referral_code: str


class RewardSummaryResponse(BaseModel):
    total_rewards: int
    active_rewards: int
    total_discount_days_available: int


@router.get("/my-code", response_model=APIResponse[str])
@standardize_response
def get_my_referral_code(
    current_user: User = Depends(get_current_user)
):
    """Get the current user's referral code"""
    if not current_user.referral_code:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return success_response(
        data=current_user.referral_code,
        message="Referral code retrieved successfully"
    )


@router.get("/stats", response_model=APIResponse[ReferralStatsResponse])
@standardize_response
def get_referral_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get referral statistics for the current user"""
    stats = referral_crud.get_referral_stats(db=db, user_id=current_user.id)
    
    response_data = ReferralStatsResponse(
        total_referrals=stats["total_referrals"],
        recent_referrals=stats["recent_referrals"],
        user_referral_code=current_user.referral_code or ""
    )
    
    return success_response(
        data=response_data,
        message="Referral statistics retrieved successfully"
    )


@router.get("/rewards", response_model=APIResponse[RewardSummaryResponse])
@standardize_response
def get_my_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reward summary for the current user"""
    reward_summary = reward_crud.get_reward_summary(db=db, user_id=current_user.id)
    
    response_data = RewardSummaryResponse(
        total_rewards=reward_summary["total_rewards"],
        active_rewards=reward_summary["active_rewards"],
        total_discount_days_available=reward_summary["total_discount_days_available"]
    )
    
    return success_response(
        data=response_data,
        message="Reward summary retrieved successfully"
    )


@router.post("/rewards/{reward_id}/use", response_model=APIResponse[dict])
@standardize_response
def use_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a reward as used"""
    try:
        used_reward = reward_crud.use_reward(
            db=db,
            reward_id=reward_id,
            user_id=current_user.id
        )
        
        return success_response(
            data={
                "reward_id": used_reward.id,
                "discount_days": used_reward.discount_days,
                "used_at": used_reward.used_at.isoformat()
            },
            message="Reward used successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error using reward: {str(e)}")


@router.get("/validate/{referral_code}", response_model=APIResponse[dict])
@standardize_response
def validate_referral_code(
    referral_code: str,
    db: Session = Depends(get_db)
):
    """Validate if a referral code exists and get basic info"""
    user = referral_crud.get_user_by_referral_code(db=db, referral_code=referral_code)
    
    if not user:
        return success_response(
            data={"valid": False, "message": "Referral code not found"},
            message="Referral code validation completed"
        )
    
    return success_response(
        data={
            "valid": True,
            "referrer_username": user.username,
            "message": f"Valid referral code from {user.username}"
        },
        message="Referral code validation completed"
    )
