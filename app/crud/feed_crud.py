from sqlalchemy.orm import Session
from app.models.feed import FeedItem
from app.schemas.feed_schema import FeedCreate

class FeedCRUD:
    def create(self, db: Session, obj_in: FeedCreate):
        feed = FeedItem(**obj_in.model_dump())
        db.add(feed)
        db.commit()
        db.refresh(feed)
        return feed

    def get_all(self, db: Session):
        return db.query(FeedItem).order_by(FeedItem.created_at.desc()).all()

    def get(self, db: Session, feed_id: int):
        return db.query(FeedItem).filter(FeedItem.id == feed_id).first()

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

feed_crud = FeedCRUD()
