from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.schemas.api_response import success_response, APIResponse
from app.services.level_service import LevelService


router = APIRouter(prefix="/users", tags=["User Levels"])


@router.get("/me/level-progress", response_model=APIResponse[dict])
@standardize_response
def get_my_level_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's level progress.
    Shows current level, conditions met, and progress toward next level.
    """
    level_service = LevelService(db)
    
    try:
        progress = level_service.get_level_progress(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return success_response(
        data=progress,
        message="Level progress retrieved successfully"
    )
