from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_, func
from app.models.product import Product, ProductCategory
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductCategoryCreate
from fastapi import HTTPException
from typing import Optional, List


class ProductCRUD:
    # Category methods
    def create_category(self, db: Session, obj_in: ProductCategoryCreate) -> ProductCategory:
        # Check if category already exists
        existing = db.query(ProductCategory).filter(ProductCategory.name == obj_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        category = ProductCategory(name=obj_in.name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    def get_category(self, db: Session, category_id: int) -> Optional[ProductCategory]:
        return db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    
    def get_all_categories(self, db: Session) -> List[ProductCategory]:
        return db.query(ProductCategory).order_by(ProductCategory.name).all()
    
    def update_category(self, db: Session, category_id: int, name: str) -> ProductCategory:
        category = self.get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if new name already exists
        existing = db.query(ProductCategory).filter(
            ProductCategory.name == name,
            ProductCategory.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
        
        category.name = name
        db.commit()
        db.refresh(category)
        return category
    
    def delete_category(self, db: Session, category_id: int):
        category = self.get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if category has products
        products_count = db.query(Product).filter(Product.category_id == category_id).count()
        if products_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete category with existing products")
        
        db.delete(category)
        db.commit()
    
    # Product methods
    def create_product(self, db: Session, obj_in: ProductCreate) -> Product:
        # Validate category exists
        category = self.get_category(db, obj_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if SKU already exists (if provided)
        if obj_in.sku:
            existing_sku = db.query(Product).filter(Product.sku == obj_in.sku).first()
            if existing_sku:
                raise HTTPException(status_code=400, detail="SKU already exists")
        
        product_data = obj_in.model_dump()
        product = Product(**product_data)
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).options(joinedload(Product.category)).offset(skip).limit(limit).all()
    
    # def get_by_category(self, db: Session, category_name: str) -> List[Product]:
    #     categories = [
    #         "Health and Dietary Suppliments",
    #         "Personal Care and Cosmetics",
    #         "Food and Beverages",
    #         "Others"
    #     ]
    
    #     if category_name not in categories:
    #         raise HTTPException(status_code=404, detail="Category not found")

    #     return (
    #         db.query(Product)
    #         .join(ProductCategory)
    #         .filter(ProductCategory.name == category_name)
    #         .options(joinedload(Product.category))
    #         .all()
    #     )
    def count_all(self, db: Session, category_name: Optional[str] = None, status: Optional[str] = None) -> int:
        query = db.query(Product).join(ProductCategory)

        categories = [
            "Health and Dietary Suppliments",
            "Personal Care and Cosmetics",
            "Food and Beverages",
            "Others"
        ]
        categories_lower = [c.lower() for c in categories]

        if category_name:
            category_name_normalized = category_name.strip().lower()

            if category_name_normalized not in categories_lower:
                raise HTTPException(status_code=404, detail="Category not found")

            if category_name_normalized == "others":
                query = query.filter(~func.lower(ProductCategory.name).in_(categories_lower))
            else:
                query = query.filter(func.lower(ProductCategory.name) == category_name_normalized)

        if status:
            query = query.filter(Product.status == status)

        return query.count()

    def get_by_category(
        self,
        db: Session,
        category_name: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Product]:
        categories = db.query(ProductCategory).all()
        category_name_normalized = category_name.strip().lower()
        print(category_name_normalized,"category_name_normalized")
        categories_lower = [c.name.lower() for c in categories]
        print(categories_lower,"categories_lower")

        if category_name_normalized not in categories_lower:
            raise HTTPException(status_code=404, detail="Category not found")

        query = db.query(Product).join(ProductCategory).options(joinedload(Product.category))

        # if category_name_normalized == "others":
        #     query = query.filter(~func.lower(ProductCategory.name).in_(categories_lower))
        # else:
        query = query.filter(func.lower(ProductCategory.name) == category_name_normalized)

        return query.offset(offset).limit(limit).all()
    
    def get_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    
    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        return db.query(Product).options(joinedload(Product.category)).filter(Product.sku == sku).first()
    
    def search_count(self, db: Session, query: str) -> int:
        """Count products matching the search query"""
        search_filter = or_(
            Product.name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%"),
            Product.company.ilike(f"%{query}%"),
            Product.tags.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%")
        )
        return db.query(Product).filter(search_filter).count()

    
    def search_products(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name, SKU, company, or tags"""
        search_filter = or_(
            Product.name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%"),
            Product.company.ilike(f"%{query}%"),
            Product.tags.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%")
        )
        
        query_builder = db.query(Product).options(joinedload(Product.category)).filter(search_filter)
        
        return query_builder.offset(skip).limit(limit).all()
    
    def get_best_sellers(self, db: Session, limit: int = 20) -> List[Product]:
        """Get products marked as best sellers"""
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.best_seller == True
        ).limit(limit).all()
    
    def get_by_status(self, db: Session, status: str) -> List[Product]:
        """Get products by status"""
        return db.query(Product).options(joinedload(Product.category)).filter(Product.status == status).all()
    
    def update_product(self, db: Session, product_id: int, obj_in: ProductUpdate) -> Product:
        product = self.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Validate category if being updated
        if "category_id" in update_data:
            category = self.get_category(db, update_data["category_id"])
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
        
        # Check SKU uniqueness if being updated
        if "sku" in update_data and update_data["sku"]:
            existing_sku = db.query(Product).filter(
                Product.sku == update_data["sku"],
                Product.id != product_id
            ).first()
            if existing_sku:
                raise HTTPException(status_code=400, detail="SKU already exists")
        
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    def delete_product(self, db: Session, product_id: int):
        product = self.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db.delete(product)
        db.commit()
    
    def update_stock(self, db: Session, product_id: int, quantity: int) -> Product:
        """Update product stock quantity"""
        product = self.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        product.quantity = quantity
        
        # Auto-update status based on quantity
        if quantity == 0:
            product.status = "out_of_stock"
        elif quantity <= 10:  # You can adjust this threshold
            product.status = "low_stock"
        else:
            product.status = "published"
        
        db.commit()
        db.refresh(product)
        return product


product_crud = ProductCRUD()
    