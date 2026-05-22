from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.desire_list import DesireListItem
from app.models.product import Product


class CRUDDesireList:
    def add_to_desire_list(self, db: Session, *, user_id: int, product_id: int) -> DesireListItem:
        """Add product to desire list or increment quantity if exists"""
        
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already exists
        query = select(DesireListItem).where(
            DesireListItem.user_id == user_id,
            DesireListItem.product_id == product_id
        )
        result = db.execute(query)
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            # Increment quantity
            existing_item.quantity += 1
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            new_item = DesireListItem(
                user_id=user_id,
                product_id=product_id,
                quantity=1
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return new_item

    def update_quantity(
        self, 
        db: Session, 
        *, 
        user_id: str, 
        product_id: int, 
        action: str
    ) -> DesireListItem:
        """Update quantity based on action (increment/decrement)"""
        
        query = select(DesireListItem).where(
            DesireListItem.user_id == user_id,
            DesireListItem.product_id == product_id
        )
        result = db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in desire list")
        
        if action == "increment":
            item.quantity += 1
        elif action == "decrement":
            if item.quantity <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Quantity cannot be less than 1. Use delete endpoint to remove item."
                )
            item.quantity -= 1
        
        db.commit()
        db.refresh(item)
        return item

    def remove_item(self, db: Session, *, user_id: int, product_id: int) -> DesireListItem:
        """Remove item from desire list"""
        
        query = select(DesireListItem).where(
            DesireListItem.user_id == user_id,
            DesireListItem.product_id == product_id
        )
        result = db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in desire list")
        
        db.delete(item)
        db.commit()
        return item

    def get_user_desire_list(self, db: Session, *, user_id: int) -> List[DesireListItem]:
        """Get all items in user's desire list with product details"""
        
        query = select(DesireListItem).where(
            DesireListItem.user_id == user_id
        ).options(
            joinedload(DesireListItem.product).joinedload(Product.category)
        ).order_by(DesireListItem.created_at.desc())
        
        result = db.execute(query)
        return result.scalars().all()

    def get_desire_list_count(self, db: Session, *, user_id: int) -> int:
        """Get count of distinct products in desire list (not quantity sum)"""
        
        query = select(func.count(DesireListItem.id)).where(
            DesireListItem.user_id == user_id
        )
        result = db.execute(query)
        count = result.scalar()
        
        return count if count else 0


desire_list_crud = CRUDDesireList()
