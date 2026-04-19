from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.crud.desire_list_crud import desire_list_crud
from app.schemas.api_response import success_response, APIResponse
from app.schemas.desire_list_schema import (
    DesireListItemCreate,
    DesireListItemUpdate,
    DesireListItemOut,
    DesireListCountResponse
)
from app.schemas.product_schema import ProductOut


router = APIRouter(prefix="/desire-list", tags=["Desire List"])


@router.post("/", response_model=APIResponse[DesireListItemOut])
@standardize_response
def add_to_desire_list(
    *,
    db: Session = Depends(get_db),
    item_in: DesireListItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Add product to desire list or increment quantity if exists"""
    item = desire_list_crud.add_to_desire_list(
        db=db,
        user_id=current_user.id,
        product_id=item_in.product_id
    )
    
    # Prepare response with product details
    item_out = DesireListItemOut(
        id=item.id,
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity,
        created_at=item.created_at,
        updated_at=item.updated_at,
        product=ProductOut.model_validate(item.product)
    )
    
    if item.product.category:
        item_out.product.category_name = item.product.category.name
    
    return success_response(
        data=item_out,
        message="Product added to desire list successfully",
        status_code=201
    )


@router.get("/", response_model=APIResponse[List[DesireListItemOut]])
@standardize_response
def get_desire_list(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's desire list with product details"""
    items = desire_list_crud.get_user_desire_list(
        db=db,
        user_id=current_user.id
    )
    
    # Prepare response with product details
    items_out = []
    for item in items:
        item_out = DesireListItemOut(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            created_at=item.created_at,
            updated_at=item.updated_at,
            product=ProductOut.model_validate(item.product)
        )
        
        if item.product.category:
            item_out.product.category_name = item.product.category.name
        
        items_out.append(item_out)
    
    return success_response(
        data=items_out,
        message="Desire list retrieved successfully"
    )


@router.get("/count", response_model=APIResponse[DesireListCountResponse])
@standardize_response
def get_desire_list_count(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total quantity sum of items in desire list"""
    count = desire_list_crud.get_desire_list_count(
        db=db,
        user_id=current_user.id
    )
    
    return success_response(
        data=DesireListCountResponse(count=count),
        message="Desire list count retrieved successfully"
    )


@router.patch("/{product_id}", response_model=APIResponse[DesireListItemOut])
@standardize_response
def update_desire_list_quantity(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    update_data: DesireListItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update quantity of item in desire list (increment/decrement)"""
    item = desire_list_crud.update_quantity(
        db=db,
        user_id=current_user.id,
        product_id=product_id,
        action=update_data.action
    )
    
    # Prepare response with product details
    item_out = DesireListItemOut(
        id=item.id,
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity,
        created_at=item.created_at,
        updated_at=item.updated_at,
        product=ProductOut.model_validate(item.product)
    )
    
    if item.product.category:
        item_out.product.category_name = item.product.category.name
    
    return success_response(
        data=item_out,
        message=f"Quantity {update_data.action}ed successfully"
    )


@router.delete("/{product_id}", response_model=APIResponse[str])
@standardize_response
def remove_from_desire_list(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """Remove item from desire list"""
    desire_list_crud.remove_item(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )
    
    return success_response(
        data="Item removed from desire list",
        message="Item removed from desire list successfully"
    )
