from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.api_response import success_response, APIResponse
from app.crud.product_crud import product_crud
from app.models.product import ProductCategory, Product
from pydantic import BaseModel, field_validator
from app.dependencies.auth_dependency import check_user_permissions
from app.models.user import UserRole, User
from app.core.decorators import standardize_response
import math

router = APIRouter(prefix="/categories",tags=["Categories"])

class CategoryCreate(BaseModel):
    name: str

class CategoryOut(CategoryCreate):
    id: int
    class Config:
        from_attributes = True

@router.post("/", response_model=APIResponse[CategoryOut])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(ProductCategory).filter_by(name=category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    cat = ProductCategory(name=category.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)

    return success_response(cat, "Category created successfully")


@router.get("/", response_model=APIResponse[list[CategoryOut]])
def list_categories(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(25, ge=1, le=25),
    db: Session = Depends(get_db)
):
    skip = (current_page - 1) * limit
    categories = db.query(ProductCategory).offset(skip).limit(limit).all()
    total_items = db.query(ProductCategory).count()
    total_pages = math.ceil(total_items / limit) if limit else 1
    return success_response(categories, "Categories fetched successfully", total_pages=total_pages)

@router.get("/{category_id}", response_model=APIResponse[CategoryOut])
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(ProductCategory).filter_by(id=category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response(cat, "Category fetched successfully")

@router.put("/{category_id}", response_model=APIResponse[CategoryOut])
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    cat = db.query(ProductCategory).filter_by(id=category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = data.name
    db.commit()
    db.refresh(cat)
    return success_response(cat, "Category updated successfully")

@router.delete("/{category_id}", response_model=APIResponse[str])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(ProductCategory).filter_by(id=category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return success_response("Category deleted", "Deleted")
