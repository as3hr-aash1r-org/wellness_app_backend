from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.models.wellness import WellnessType
from app.crud.wellness_crud import wellness_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.wellness_schema import (
    WellnessCreate, WellnessUpdate, WellnessRead, WellnessStatsResponse
)

router = APIRouter(prefix="/wellness", tags=["Wellness"])


# Admin Routes
@router.post("/", response_model=APIResponse[WellnessRead])
@standardize_response
def create_wellness(
    *,
    db: Session = Depends(get_db),
    wellness_in: WellnessCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new wellness activity (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create wellness activities")
    
    wellness = wellness_crud.create_wellness(db=db, obj_in=wellness_in)
    return success_response(
        data=wellness,
        message="Wellness activity created successfully",
        status_code=201
    )


@router.get("/", response_model=APIResponse[List[WellnessRead]])
@standardize_response
def get_all_wellness(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all wellness activities with pagination"""
    wellness_list = wellness_crud.get_all_wellness(db=db, skip=skip, limit=limit)
    return success_response(
        data=wellness_list,
        message="Wellness activities retrieved successfully"
    )


@router.get("/type/{wellness_type}", response_model=APIResponse[List[WellnessRead]])
@standardize_response
def get_wellness_by_type(
    wellness_type: WellnessType,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all wellness activities by type (exercise, therapy, stress)"""
    wellness_list = wellness_crud.get_wellness_by_type(
        db=db, wellness_type=wellness_type, skip=skip, limit=limit
    )
    return success_response(
        data=wellness_list,
        message=f"{wellness_type.value.title()} activities retrieved successfully"
    )


@router.get("/search", response_model=APIResponse[List[WellnessRead]])
@standardize_response
def search_wellness(
    q: str = Query(..., min_length=1, description="Search query"),
    wellness_type: Optional[WellnessType] = Query(None),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Search wellness activities by title or benefits"""
    wellness_list = wellness_crud.search_wellness(
        db=db, query=q, wellness_type=wellness_type, skip=skip, limit=limit
    )
    return success_response(
        data=wellness_list,
        message=f"Search results for '{q}' retrieved successfully"
    )


@router.get("/{wellness_id}", response_model=APIResponse[WellnessRead])
@standardize_response
def get_wellness_by_id(
    wellness_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific wellness activity by ID"""
    wellness = wellness_crud.get_wellness_by_id(db=db, wellness_id=wellness_id)
    if not wellness:
        raise HTTPException(status_code=404, detail="Wellness activity not found")
    
    return success_response(
        data=wellness,
        message="Wellness activity retrieved successfully"
    )


@router.put("/{wellness_id}", response_model=APIResponse[WellnessRead])
@standardize_response
def update_wellness(
    wellness_id: int,
    *,
    db: Session = Depends(get_db),
    wellness_in: WellnessUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a wellness activity (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update wellness activities")
    
    wellness = wellness_crud.update_wellness(db=db, wellness_id=wellness_id, obj_in=wellness_in)
    return success_response(
        data=wellness,
        message="Wellness activity updated successfully"
    )


@router.delete("/{wellness_id}", response_model=APIResponse[WellnessRead])
@standardize_response
def delete_wellness(
    wellness_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a wellness activity (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete wellness activities")
    
    wellness = wellness_crud.delete_wellness(db=db, wellness_id=wellness_id)
    return success_response(
        data=wellness,
        message="Wellness activity deleted successfully"
    )


@router.get("/stats/count-by-type", response_model=APIResponse[WellnessStatsResponse])
@standardize_response
def get_wellness_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get wellness statistics by type (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view wellness statistics")
    
    stats = wellness_crud.get_wellness_stats(db=db)
    
    response_data = WellnessStatsResponse(
        total_wellness=stats["total_wellness"],
        exercise_count=stats["exercise_count"],
        therapy_count=stats["therapy_count"],
        stress_count=stats["stress_count"]
    )
    
    return success_response(
        data=response_data,
        message="Wellness statistics retrieved successfully"
    )
