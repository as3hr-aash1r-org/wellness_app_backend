from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import openpyxl
from io import BytesIO

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.models.fact import FactType
from app.crud.fact_crud import fact_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.fact_schema import (
    FactCreate, 
    FactUpdate, 
    FactRead, 
    BulkUploadResponse,
    UserFactLibraryOut
)
import math


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


@router.post("/bulk-upload", response_model=APIResponse[BulkUploadResponse])
@standardize_response
def bulk_upload_facts(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload facts from Excel file (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload facts")
    
    # Validate file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only .xlsx or .xls files are allowed")
    
    try:
        # Read Excel file
        contents = file.file.read()
        workbook = openpyxl.load_workbook(BytesIO(contents), read_only=True)
        sheet = workbook.active
        
        # Parse rows (skip header)
        facts_data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not any(row):  # Skip empty rows
                continue
            
            facts_data.append({
                'title': row[0] if len(row) > 0 else None,
                'description': row[1] if len(row) > 1 else None,
                'type': row[2] if len(row) > 2 else None
            })
        
        if not facts_data:
            raise HTTPException(status_code=400, detail="No valid data found in Excel file")
        
        # Bulk create
        result = fact_crud.bulk_create_facts(db=db, facts_data=facts_data)
        
        return success_response(
            data=BulkUploadResponse(**result),
            message="Bulk upload complete",
            status_code=201
        )
        
    except openpyxl.utils.exceptions.InvalidFileException:
        raise HTTPException(status_code=400, detail="Invalid Excel file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        file.file.close()


@router.get("/", response_model=APIResponse[List[FactRead]])
@standardize_response
def get_all_facts(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all facts with pagination"""
    skip = (current_page - 1) * limit
    facts = fact_crud.get_all_facts(db=db, skip=skip, limit=limit)
    total_items = fact_crud.count_all_facts(db=db)
    total_pages = math.ceil(total_items / limit) if limit else 1
    return success_response(
        data=facts,
        message="Facts retrieved successfully",
        total_pages=total_pages
    )


@router.get("/type/{fact_type}", response_model=APIResponse[List[FactRead]])
@standardize_response
def get_facts_by_type(
    fact_type: FactType,
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all facts by type (gut, nutrition, sleep) with pagination"""
    skip = (current_page - 1) * limit
    facts = fact_crud.get_facts_by_type(db=db, fact_type=fact_type, skip=skip, limit=limit)
    total_items = fact_crud.count_facts_by_type(db=db, fact_type=fact_type)
    total_pages = math.ceil(total_items / limit) if limit else 1
    return success_response(
        data=facts,
        message=f"{fact_type.value.title()} facts retrieved successfully",
        total_pages=total_pages
    )


@router.get("/tip-of-the-day/{fact_type}", response_model=APIResponse[FactRead])
@standardize_response
def get_tip_of_the_day(
    fact_type: FactType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current tip of the day for a specific type.
    Returns empty if user has already read a tip today (UTC, strictly 1 per day).
    """
    tip = fact_crud.get_tip_of_the_day(db=db, fact_type=fact_type, user_id=current_user.id)
    
    if not tip:
        return success_response(
            data=None,
            message=f"Your viewed tips are already in your Library"
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
    """Delete a fact (Admin only) - cascades to user libraries"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete facts")
    
    fact = fact_crud.delete_fact(db=db, fact_id=fact_id)
    return success_response(
        data=fact,
        message="Fact deleted successfully"
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
        stats[fact_type.value] = fact_crud.count_facts_by_type(db=db, fact_type=fact_type)
    
    return success_response(
        data=stats,
        message="Facts count by type retrieved successfully"
    )


# User Fact Library Endpoints

@router.post("/{fact_id}/save-to-library", response_model=APIResponse[UserFactLibraryOut])
@standardize_response
def save_fact_to_library(
    fact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save fact to user's library (idempotent - triggered by 'Read More' tap)"""
    library_entry = fact_crud.save_to_library(
        db=db,
        user_id=current_user.id,
        fact_id=fact_id
    )
    
    return success_response(
        data=library_entry,
        message="Fact saved to library successfully"
    )


@router.get("/library", response_model=APIResponse[List[UserFactLibraryOut]])
@standardize_response
def get_user_fact_library(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's fact library (all saved facts)"""
    skip = (current_page - 1) * limit
    library = fact_crud.get_user_library(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    total_items = fact_crud.count_user_library(db=db, user_id=current_user.id)
    total_pages = math.ceil(total_items / limit) if limit else 1
    
    return success_response(
        data=library,
        message="Fact library retrieved successfully",
        total_pages=total_pages
    )


@router.get("/library/type/{fact_type}", response_model=APIResponse[List[UserFactLibraryOut]])
@standardize_response
def get_user_fact_library_by_type(
    fact_type: FactType,
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's fact library filtered by type"""
    skip = (current_page - 1) * limit
    library = fact_crud.get_user_library(
        db=db,
        user_id=current_user.id,
        fact_type=fact_type,
        skip=skip,
        limit=limit
    )
    total_items = fact_crud.count_user_library(
        db=db,
        user_id=current_user.id,
        fact_type=fact_type
    )
    total_pages = math.ceil(total_items / limit) if limit else 1
    
    return success_response(
        data=library,
        message=f"{fact_type.value.title()} facts from library retrieved successfully",
        total_pages=total_pages
    )
