from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User, AppLevel
from app.schemas.api_response import success_response, APIResponse
from app.services.level_service import LevelService


router = APIRouter(prefix="/admin/users", tags=["Admin - User Levels"])


class SetLevelRequest(BaseModel):
    level: AppLevel


@router.patch("/{user_id}/level", response_model=APIResponse[dict])
@standardize_response
def set_user_level(
    user_id: int,
    request: SetLevelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set user level (Admin only).
    Allows any level change including downgrades.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change user levels")
    
    level_service = LevelService(db)
    
    try:
        user = level_service.set_level(user_id, request.level)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    db.commit()
    
    return success_response(
        data={
            "user_id": user.id,
            "username": user.username,
            "app_level": user.app_level.value,
            "level_upgraded_at": user.level_upgraded_at.isoformat() if user.level_upgraded_at else None
        },
        message=f"User level updated to {request.level.value}"
    )
