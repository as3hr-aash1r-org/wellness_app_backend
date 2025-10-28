from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.product_schema import ProductCreate, ProductOut, ProductUpdate
from app.schemas.api_response import success_response, APIResponse
from app.crud.product_crud import product_crud
from app.dependencies.auth_dependency import check_user_permissions, get_current_user
from app.models.user import UserRole, User
from app.core.decorators import standardize_response
import math

router = APIRouter(prefix="/products", tags=["Products"])


# Product Routes
@router.post("/", response_model=APIResponse[ProductOut])
@standardize_response
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Create a new product - Admin only"""
    try:
        product = product_crud.create_product(db=db, obj_in=product_data)
        product_out = ProductOut.model_validate(product)
        if product.category:
            product_out.category_name = product.category.name
        return success_response(
            data=product_out,
            message="Product created successfully",
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.get("/", response_model=APIResponse[List[ProductOut]])
@standardize_response
def get_all_products(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(100, ge=1, le=100),
    category_name: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get products with filtering options"""
    try:
        offset = (current_page - 1) * limit
        if search:
            products = product_crud.search_products(db=db, query=search,skip=offset, limit=limit)
            total_items = product_crud.search_count(db=db, query=search)
        elif category_name:
            products = product_crud.get_by_category(db=db, category_name=category_name, offset=offset, limit=limit)
            print(products,"products")
            print(category_name,"category_name")
            total_items = product_crud.count_all(db=db, category_name=category_name)
        else:
            products = product_crud.get_all(db=db, skip=offset, limit=limit)
            total_items = product_crud.count_all(db=db)
        
        total_pages = math.ceil(total_items / limit) if limit else 1
        # Add category names
        product_outs = []
        for product in products:
            product_out = ProductOut.model_validate(product)
            if product.category:
                product_out.category_name = product.category.name
            product_outs.append(product_out)
        
        return success_response(
            data=product_outs,
            message="Products fetched successfully",
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


# @router.get("/search", response_model=APIResponse[List[ProductOut]])
# @standardize_response
# def search_products(
#     q: str = Query(..., min_length=1, description="Search query"),
#     category_id: Optional[int] = Query(None),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=100),
#     db: Session = Depends(get_db)
# ):
#     """Search products by name, SKU, company, tags, or description"""
#     products = product_crud.search_products(
#         db=db, query=q, category_id=category_id, skip=skip, limit=limit
#     )
    
#     # Add category names
#     product_outs = []
#     for product in products:
#         product_out = ProductOut.model_validate(product)
#         if product.category:
#             product_out.category_name = product.category.name
#         product_outs.append(product_out)
    
#     return success_response(
#         data=product_outs,
#         message="Search results fetched successfully"
#     )


@router.get("/sku/{sku}", response_model=APIResponse[ProductOut])
@standardize_response
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Get product by SKU"""
    product = product_crud.get_by_sku(db=db, sku=sku.upper())
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_out = ProductOut.model_validate(product)
    if product.category:
        product_out.category_name = product.category.name
    
    return success_response(
        data=product_out,
        message="Product fetched successfully"
    )


@router.get("/{product_id}", response_model=APIResponse[ProductOut])
@standardize_response
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = product_crud.get_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_out = ProductOut.model_validate(product)
    if product.category:
        product_out.category_name = product.category.name
    
    return success_response(
        data=product_out,
        message="Product fetched successfully"
    )


@router.put("/{product_id}", response_model=APIResponse[ProductOut])
@standardize_response
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Update product - Admin only"""
    try:
        product = product_crud.update_product(db=db, product_id=product_id, obj_in=product_data)
        product_out = ProductOut.model_validate(product)
        if product.category:
            product_out.category_name = product.category.name
        
        return success_response(
            data=product_out,
            message="Product updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


@router.patch("/{product_id}/stock", response_model=APIResponse[ProductOut])
@standardize_response
def update_product_stock(
    product_id: int,
    quantity: int = Query(..., ge=0, description="New stock quantity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Update product stock quantity - Admin only"""
    try:
        product = product_crud.update_stock(db=db, product_id=product_id, quantity=quantity)
        product_out = ProductOut.model_validate(product)
        if product.category:
            product_out.category_name = product.category.name
        
        return success_response(
            data=product_out,
            message="Product stock updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stock: {str(e)}")


@router.delete("/{product_id}", response_model=APIResponse[str])
@standardize_response
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Delete product - Admin only"""
    try:
        product_crud.delete_product(db=db, product_id=product_id)
        return success_response(
            data="Product deleted successfully",
            message="Product deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")
