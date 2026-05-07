from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import date
from typing import Optional

from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions
from app.models.user import User, UserRole
from app.models.submission import Submission, SubmissionStatus
from app.models.referrals import Referrals
from app.schemas.api_response import APIResponse, success_response
from app.core.decorators import standardize_response


router = APIRouter(prefix="/influencer/analytics", tags=["Influencer Analytics"])


@router.get("/dashboard", response_model=APIResponse[dict])
@standardize_response
def get_dashboard_stats(
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.influencer))
):
    """
    Get influencer dashboard analytics.
    Returns total submissions, approval rate, active influencers, referrals, and platform stats.
    """
    
    # Build base filter conditions
    filters = [Submission.influencer_id == current_user.id]
    if from_date:
        filters.append(Submission.created_at >= from_date)
    if to_date:
        filters.append(Submission.created_at <= to_date)
    
    # 1. Total Submissions
    total_submissions = db.execute(
        select(func.count(Submission.id)).where(and_(*filters))
    ).scalar() or 0
    
    # 2. Approved Submissions Count
    approved_count = db.execute(
        select(func.count(Submission.id)).where(
            and_(*filters, Submission.status == SubmissionStatus.approved)
        )
    ).scalar() or 0
    
    # Calculate approval rate
    approval_rate = round((approved_count / total_submissions * 100), 2) if total_submissions > 0 else 0
    
    # 3. Active Influencers (total count in system)
    active_influencers = db.execute(
        select(func.count(User.id))
        .where(User.role == UserRole.influencer)
        .where((User.is_deleted == False) | (User.is_deleted == None))
    ).scalar() or 0
    
    # 4. Total Referrals
    total_referrals = db.execute(
        select(func.count(Referrals.id))
        .where(Referrals.referrer_user_id == current_user.id)
    ).scalar() or 0
    
    # 5. Platform Stats
    platform_stats_query = select(
        Submission.platform,
        func.count(Submission.id).label('total_posts')
    ).where(and_(*filters)).group_by(Submission.platform)
    
    platform_results = db.execute(platform_stats_query).all()
    
    platform_stats = []
    for platform, total_posts in platform_results:
        # Get approved count for this platform
        approved_for_platform = db.execute(
            select(func.count(Submission.id)).where(
                and_(
                    *filters,
                    Submission.platform == platform,
                    Submission.status == SubmissionStatus.approved
                )
            )
        ).scalar() or 0
        
        approval_percentage = round((approved_for_platform / total_posts * 100), 2) if total_posts > 0 else 0
        
        platform_stats.append({
            "platform": platform,
            "total_posts": total_posts,
            "approval_percentage": approval_percentage
        })
    
    return success_response(
        data={
            "total_submissions": total_submissions,
            "approval_rate": approval_rate,
            "active_influencers": active_influencers,
            "total_referrals": total_referrals,
            "platform_stats": platform_stats
        },
        message="Dashboard stats fetched successfully"
    )
