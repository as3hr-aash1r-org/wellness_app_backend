from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.product_schema import ProductCreate, ProductOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.product_crud import product_crud
from fastapi import HTTPException


router = APIRouter(prefix="/products",tags=["Products"])

@router.post("/",response_model=APIResponse[ProductOut])
def create_product(product_data:ProductCreate,db:Session = Depends(get_db)):
    category = product_crud.get_category(db=db,category_id=product_data.category_id)
    if not category:
        raise HTTPException(status_code=404,detail="Category not found")
    product = product_crud.create_product(db = db,obj_in=product_data)
    return success_response(
        data=ProductOut.model_validate(product),
        message="Product created successfully"
    )

@router.get("/",response_model=APIResponse[list[ProductOut]])
def get_all_products(db:Session = Depends(get_db)):
    products = product_crud.get_all(db=db)
    return success_response(
        data=[ProductOut.model_validate(product) for product in products],
        message="Products fetched successfully"
    )

@router.get("/{product_id}", response_model=APIResponse[ProductOut])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return success_response(ProductOut.model_validate(product), "Product fetched successfully")

@router.put("/{product_id}", response_model=APIResponse[ProductOut])
def update_product(product_id: int, data: ProductCreate, db: Session = Depends(get_db)):
    updated = product_crud.update_product(db, product_id, data.model_dump())
    return success_response(ProductOut.model_validate(updated), "Product updated successfully")

@router.delete("/{product_id}", response_model=APIResponse[str])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_crud.delete_product(db, product_id)
    return success_response("Product deleted successfully", "Deleted")