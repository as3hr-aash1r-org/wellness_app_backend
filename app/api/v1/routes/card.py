from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User, UserRole
from app.schemas.card_schema import (
    CardCreate, CardUpdate, CardOut,
    CardTypeCreate, CardTypeUpdate, CardTypeOut
)
from app.schemas.api_response import success_response, APIResponse
from app.crud.card_crud import card_crud, card_type_crud
from app.core.decorators import standardize_response


router = APIRouter(prefix="/cards", tags=["Cards"])


def check_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user



@router.get("/", response_model=APIResponse[List[CardOut]])
@standardize_response
def get_cards_by_type(
    type: str = Query(..., description="Card type name to filter by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all cards by type name (App-facing).
    Returns all cards matching the specified type.
    """
    cards = card_crud.get_by_type_name(db, type_name=type)
    return success_response(
        data=cards,
        message=f"Cards of type '{type}' fetched successfully"
    )



@router.post("/types", response_model=APIResponse[CardTypeOut])
@standardize_response
def create_card_type(
    card_type_data: CardTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Create a new card type (Admin only).
    E.g., "fundamental", "new_joiners", "prospectus"
    """
    card_type = card_type_crud.create(db, obj_in=card_type_data)
    return success_response(
        data=card_type,
        message="Card type created successfully",
        status_code=201
    )


@router.get("/types", response_model=APIResponse[List[CardTypeOut]])
@standardize_response
def get_all_card_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Get all card types (Admin only).
    """
    card_types = card_type_crud.get_all(db, skip=skip, limit=limit)
    return success_response(
        data=card_types,
        message="Card types fetched successfully"
    )


@router.get("/types/{card_type_id}", response_model=APIResponse[CardTypeOut])
@standardize_response
def get_card_type(
    card_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Get card type by ID (Admin only).
    """
    card_type = card_type_crud.get_by_id(db, card_type_id=card_type_id)
    if not card_type:
        raise HTTPException(status_code=404, detail="Card type not found")
    
    return success_response(
        data=card_type,
        message="Card type fetched successfully"
    )


@router.put("/types/{card_type_id}", response_model=APIResponse[CardTypeOut])
@standardize_response
def update_card_type(
    card_type_id: int,
    card_type_data: CardTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Update card type (Admin only).
    """
    card_type = card_type_crud.update(db, card_type_id=card_type_id, obj_in=card_type_data)
    return success_response(
        data=card_type,
        message="Card type updated successfully"
    )


@router.delete("/types/{card_type_id}", response_model=APIResponse[str])
@standardize_response
def delete_card_type(
    card_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Delete card type (Admin only).
    Cascades to all cards under this type.
    """
    card_type_crud.delete(db, card_type_id=card_type_id)
    return success_response(
        data="Card type deleted successfully",
        message="Card type and all associated cards deleted successfully"
    )

@router.post("/", response_model=APIResponse[CardOut])
@standardize_response
def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Create a new card (Admin only).
    Upload HTML content for a specific card type.
    """
    card = card_crud.create(db, obj_in=card_data)
    return success_response(
        data=card,
        message="Card created successfully",
        status_code=201
    )


@router.get("/content", response_model=APIResponse[List[CardOut]])
@standardize_response
def get_all_cards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Get all cards (Admin only).
    Returns all cards across all types.
    """
    cards = card_crud.get_all(db, skip=skip, limit=limit)
    return success_response(
        data=cards,
        message="All cards fetched successfully"
    )


@router.get("/{card_id}", response_model=APIResponse[CardOut])
@standardize_response
def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Get card by ID (Admin only).
    """
    card = card_crud.get_by_id(db, card_id=card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return success_response(
        data=card,
        message="Card fetched successfully"
    )


@router.put("/{card_id}", response_model=APIResponse[CardOut])
@standardize_response
def update_card(
    card_id: int,
    card_data: CardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Update card content (Admin only).
    Re-upload HTML content for an existing card.
    """
    card = card_crud.update(db, card_id=card_id, obj_in=card_data)
    return success_response(
        data=card,
        message="Card updated successfully"
    )


@router.delete("/{card_id}", response_model=APIResponse[str])
@standardize_response
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Delete a card (Admin only).
    """
    card_crud.delete(db, card_id=card_id)
    return success_response(
        data="Card deleted successfully",
        message="Card deleted successfully"
    )
