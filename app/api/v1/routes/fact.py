from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.models.fact import FactType
from app.crud.fact_crud import fact_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.fact_schema import FactCreate, FactUpdate, FactRead


router = APIRouter(prefix="/facts", tags=["Facts"])


@router.post("/", response_model=APIResponse[FactRead])
@standardize_response
def create_fact(
    *,
    db: Session = Depends(get_db),
    fact_in: FactCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new fact (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create facts")
    
    fact = fact_crud.create_fact(db=db, obj_in=fact_in)
    return success_response(
        data=fact,
        message="Fact created successfully",
        status_code=201
    )


@router.get("/", response_model=APIResponse[List[FactRead]])
@standardize_response
def get_all_facts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all facts with pagination"""
    facts = fact_crud.get_all_facts(db=db, skip=skip, limit=limit)
    return success_response(
        data=facts,
        message="Facts retrieved successfully"
    )


@router.get("/type/{fact_type}", response_model=APIResponse[List[FactRead]])
@standardize_response
def get_facts_by_type(
    fact_type: FactType,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all facts by type (gut, nutrition, sleep) with pagination"""
    facts = fact_crud.get_facts_by_type(db=db, fact_type=fact_type, skip=skip, limit=limit)
    return success_response(
        data=facts,
        message=f"{fact_type.value.title()} facts retrieved successfully"
    )


@router.get("/tip-of-the-day/{fact_type}", response_model=APIResponse[FactRead])
@standardize_response
def get_tip_of_the_day(
    fact_type: FactType,
    db: Session = Depends(get_db)
):
    """Get the current tip of the day for a specific type"""
    tip = fact_crud.get_tip_of_the_day(db=db, fact_type=fact_type)
    
    if not tip:
        raise HTTPException(
            status_code=404, 
            detail=f"No tip of the day found for {fact_type.value}"
        )
    
    return success_response(
        data=tip,
        message=f"Tip of the day for {fact_type.value} retrieved successfully"
    )


@router.get("/{fact_id}", response_model=APIResponse[FactRead])
@standardize_response
def get_fact_by_id(
    fact_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific fact by ID"""
    fact = fact_crud.get_fact_by_id(db=db, fact_id=fact_id)
    
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    
    return success_response(
        data=fact,
        message="Fact retrieved successfully"
    )


@router.put("/{fact_id}", response_model=APIResponse[FactRead])
@standardize_response
def update_fact(
    fact_id: int,
    *,
    db: Session = Depends(get_db),
    fact_in: FactUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a fact (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update facts")
    
    fact = fact_crud.update_fact(db=db, fact_id=fact_id, obj_in=fact_in)
    return success_response(
        data=fact,
        message="Fact updated successfully"
    )


@router.delete("/{fact_id}", response_model=APIResponse[FactRead])
@standardize_response
def delete_fact(
    fact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a fact (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete facts")
    
    fact = fact_crud.delete_fact(db=db, fact_id=fact_id)
    return success_response(
        data=fact,
        message="Fact deleted successfully"
    )


@router.post("/{fact_id}/set-tip-of-the-day", response_model=APIResponse[FactRead])
@standardize_response
def set_tip_of_the_day(
    fact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a specific fact as tip of the day for its type (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can set tip of the day")
    
    fact = fact_crud.set_tip_of_the_day(db=db, fact_id=fact_id)
    return success_response(
        data=fact,
        message=f"Fact set as tip of the day for {fact.type.value} successfully"
    )


@router.get("/stats/count-by-type", response_model=APIResponse[dict])
@standardize_response
def get_facts_count_by_type(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of facts by type (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view stats")
    
    stats = {}
    for fact_type in FactType:
        stats[fact_type.value] = fact_crud.get_facts_count_by_type(db=db, fact_type=fact_type)
    
    return success_response(
        data=stats,
        message="Facts count by type retrieved successfully"
    )
