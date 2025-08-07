from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions, get_current_user
from app.models.user import UserRole, User
from app.crud.user_crud import user_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import ExpertCreate, ExpertRead, ExpertUpdate

router = APIRouter(prefix="/experts", tags=["Experts"])


@router.post("/", response_model=APIResponse[ExpertRead])
@standardize_response
def create_expert(
    expert_data: ExpertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Create a new expert - Admin only"""
    try:
        expert = user_crud.create_expert(db=db, obj_in=expert_data)
        return success_response(
            data=ExpertRead.model_validate(expert),
            message="Expert created successfully",
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expert: {str(e)}")


@router.get("/", response_model=APIResponse[List[ExpertRead]])
@standardize_response
def get_all_experts(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Get all experts - Admin only"""
    experts = user_crud.get_all_experts(db=db)
    return success_response(
        data=[ExpertRead.model_validate(expert) for expert in experts],
        message="Experts fetched successfully"
    )


@router.get("/{expert_id}", response_model=APIResponse[ExpertRead])
@standardize_response
def get_expert(
    expert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Get expert by ID - Admin only"""
    expert = user_crud.get_expert_by_id(db=db, expert_id=expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    return success_response(
        data=ExpertRead.model_validate(expert),
        message="Expert fetched successfully"
    )


@router.put("/{expert_id}", response_model=APIResponse[ExpertRead])
@standardize_response
def update_expert(
    expert_id: int,
    expert_data: ExpertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Update expert - Admin only"""
    try:
        expert = user_crud.update_expert(db=db, expert_id=expert_id, obj_in=expert_data)
        return success_response(
            data=ExpertRead.model_validate(expert),
            message="Expert updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating expert: {str(e)}")


@router.delete("/{expert_id}", response_model=APIResponse[str])
@standardize_response
def delete_expert(
    expert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Delete expert - Admin only"""
    try:
        user_crud.delete_expert(db=db, expert_id=expert_id)
        return success_response(
            data="Expert deleted successfully",
            message="Expert deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting expert: {str(e)}")


@router.get("/search/", response_model=APIResponse[List[ExpertRead]])
@standardize_response
def search_experts(
    q: Optional[str] = Query(None, description="Search query for expert name, phone, or email"),
    country: Optional[str] = Query(None, description="Filter by country"),
    position: Optional[str] = Query(None, description="Filter by position"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Search experts with filters - Admin only"""
    # This is a basic implementation - you can enhance it with more sophisticated search
    experts = user_crud.get_all_experts(db=db)
    
    # Apply filters
    if q:
        q_lower = q.lower()
        experts = [
            e for e in experts
            if (e.first_name and q_lower in e.first_name.lower()) or
               (e.last_name and q_lower in e.last_name.lower()) or
               (e.phone_number and q_lower in e.phone_number.lower()) or
               (e.email and q_lower in e.email.lower())
        ]
    
    if country:
        experts = [e for e in experts if e.country and e.country.lower() == country.lower()]
        
    if position:
        experts = [e for e in experts if e.position and e.position.lower() == position.lower()]
    
    return success_response(
        data=[ExpertRead.model_validate(expert) for expert in experts],
        message="Experts search results"
    )
