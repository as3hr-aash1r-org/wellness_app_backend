from sqlalchemy.orm import Session
from app.models.product import Product, ProductCategory
from app.schemas.product_schema import ProductCreate
from fastapi import HTTPException

class ProductCRUD:
    def get_category(self, db: Session, category_id: int):
        return db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    
    def get_by_category(self, db: Session, category_id: int):
        return db.query(Product).filter(Product.category_id == category_id).all()

    def create_product(self,db:Session,obj_in:ProductCreate):
        product = Product(**obj_in.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def get_all(self, db: Session):
        return db.query(Product).all()

    def get_by_id(self, db: Session, product_id: int):
        return db.query(Product).filter(Product.id == product_id).first()

    def update_product(self, db: Session, product_id: int, data: dict):
        product = self.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in data.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product_id: int):
        product = self.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()


product_crud = ProductCRUD()
    