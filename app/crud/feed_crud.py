from sqlalchemy.orm import Session, joinedload
from app.models.feed import FeedItem, FeedCategory
from app.schemas.feed_schema import FeedCreate, FeedCategoryCreate
from typing import Optional, List

class FeedCRUD:
    def create(self, db: Session, obj_in: FeedCreate):
        feed = FeedItem(**obj_in.model_dump())
        db.add(feed)
        db.commit()
        db.refresh(feed)
        return feed

    def get_all(self, db: Session, type: Optional[str] = None, category_id: Optional[int] = None, limit: int = 50, offset: int = 0):
        query = db.query(FeedItem).options(joinedload(FeedItem.category))
        
        if type:
            query = query.filter(FeedItem.type == type)
        if category_id:
            query = query.filter(FeedItem.category_id == category_id)
            
        return query.order_by(FeedItem.created_at.desc()).offset(offset).limit(limit).all()

    def get_featured(self, db: Session, limit: int = 10):
        return db.query(FeedItem).options(joinedload(FeedItem.category)).filter(
            FeedItem.is_featured == True
        ).order_by(FeedItem.created_at.desc()).limit(limit).all()

    def get_by_category(self, db: Session, category_id: int, limit: int = 50, offset: int = 0):
        return db.query(FeedItem).options(joinedload(FeedItem.category)).filter(
            FeedItem.category_id == category_id
        ).order_by(FeedItem.created_at.desc()).offset(offset).limit(limit).all()

    def search(self, db: Session, query: str, category_id: Optional[int] = None, limit: int = 20, offset: int = 0):
        search_query = db.query(FeedItem).options(joinedload(FeedItem.category))
        
        # Search in title, description, content, and tags
        search_filter = (
            FeedItem.title.ilike(f"%{query}%") |
            FeedItem.description.ilike(f"%{query}%") |
            FeedItem.content.ilike(f"%{query}%") |
            FeedItem.tags.ilike(f"%{query}%")
        )
        
        search_query = search_query.filter(search_filter)
        
        if category_id:
            search_query = search_query.filter(FeedItem.category_id == category_id)
            
        return search_query.order_by(FeedItem.created_at.desc()).offset(offset).limit(limit).all()

    def get(self, db: Session, feed_id: int):
        return db.query(FeedItem).options(joinedload(FeedItem.category)).filter(
            FeedItem.id == feed_id
        ).first()

    def count_all(self, db: Session, category_id: Optional[int] = None):
        query = db.query(FeedItem)
        if category_id:
            query = query.filter(FeedItem.category_id == category_id)
        return query.count()

    def search_count(self, db: Session, query: str, category_id: Optional[int] = None):
        q = db.query(FeedItem)

        search_filter = (
            FeedItem.title.ilike(f"%{query}%") |
            FeedItem.description.ilike(f"%{query}%") |
            FeedItem.content.ilike(f"%{query}%") |
            FeedItem.tags.ilike(f"%{query}%")
        )
        q = q.filter(search_filter)

        if category_id:
            q = q.filter(FeedItem.category_id == category_id)

        return q.count()


    def update(self, db: Session, feed_id: int, obj_in: FeedCreate):
        feed = self.get(db, feed_id)
        if not feed:
            return None
        for key, value in obj_in.model_dump().items():
            setattr(feed, key, value)
        db.commit()
        db.refresh(feed)
        return feed

    def delete(self, db: Session, feed_id: int):
        feed = self.get(db, feed_id)
        if feed:
            db.delete(feed)
            db.commit()
        return feed

class FeedCategoryCRUD:
    def create(self, db: Session, obj_in: FeedCategoryCreate):
        category = FeedCategory(**obj_in.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_all(self, db: Session):
        return db.query(FeedCategory).order_by(FeedCategory.name).all()

    def get(self, db: Session, category_id: int):
        return db.query(FeedCategory).filter(FeedCategory.id == category_id).first()

    def get_by_name(self, db: Session, name: str):
        return db.query(FeedCategory).filter(FeedCategory.name == name).first()

    def update(self, db: Session, category_id: int, obj_in: FeedCategoryCreate):
        category = self.get(db, category_id)
        if not category:
            return None
        for key, value in obj_in.model_dump().items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category_id: int):
        category = self.get(db, category_id)
        if category:
            db.delete(category)
            db.commit()
        return category

feed_crud = FeedCRUD()
feed_category_crud = FeedCategoryCRUD()
