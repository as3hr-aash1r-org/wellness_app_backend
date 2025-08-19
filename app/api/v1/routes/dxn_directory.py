from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.dxn_directory_schema import DXNDirectoryCreate, DXNDirectoryUpdate, DXNDirectoryOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.dxn_directory_crud import dxn_directory_crud
import math

router = APIRouter(prefix="/dxn-directory", tags=["DXN Directory"])

@router.post("/", response_model=APIResponse[DXNDirectoryOut])
def create_entry(entry: DXNDirectoryCreate, db: Session = Depends(get_db)):
    created = dxn_directory_crud.create(db, entry)
    return success_response(created, "Entry created successfully", status_code=201)

@router.get("/", response_model=APIResponse[List[DXNDirectoryOut]])
def list_entries(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    province_state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    skip = (current_page - 1) * limit
    filters = {"country": country, "city": city, "province_state": province_state}
    entries = dxn_directory_crud.search_filter_paginate(db, search, filters, skip, limit)
    total_items = dxn_directory_crud.count(db, search, filters)
    total_pages = math.ceil(total_items / limit) if limit else 1
    return success_response(entries, "Entries fetched successfully", total_pages=total_pages)

@router.get("/{entry_id}", response_model=APIResponse[DXNDirectoryOut])
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = dxn_directory_crud.get(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return success_response(entry, "Entry fetched successfully")

@router.put("/{entry_id}", response_model=APIResponse[DXNDirectoryOut])
def update_entry(entry_id: int, entry_in: DXNDirectoryUpdate, db: Session = Depends(get_db)):
    updated = dxn_directory_crud.update(db, entry_id, entry_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    return success_response(updated, "Entry updated successfully")

@router.delete("/{entry_id}", response_model=APIResponse[str])
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    deleted = dxn_directory_crud.delete(db, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return success_response("Entry deleted", "Entry deleted successfully")
