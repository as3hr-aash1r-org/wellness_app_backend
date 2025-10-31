from sqlalchemy.orm import Session, joinedload
from app.models.notifications import Notifications
from app.schemas.notification_schema import NotificationCreate

class NotificationCRUD:
    def create(self, db: Session, obj_in: NotificationCreate):
        notification = Notifications(**obj_in.model_dump())
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Notifications).order_by(Notifications.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_all(self, db: Session):
        return db.query(Notifications).count()

    def get(self, db: Session, notification_id: int):
        return db.query(Notifications).filter(Notifications.id == notification_id).first()

    def get_all_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Notifications).options(joinedload(Notifications.sender)).filter(
            Notifications.target_user_id == user_id
        ).order_by(Notifications.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_for_user(self, db: Session, user_id: int):
        return db.query(Notifications).filter(Notifications.target_user_id == user_id).count()

    def update(self, db: Session, notification_id: int, obj_in: NotificationCreate):
        notification = self.get(db, notification_id)
        if not notification:
            return None
        for key, value in obj_in.model_dump().items():
            setattr(notification, key, value)
        db.commit()
        db.refresh(notification)
        return notification

    def delete(self, db: Session, notification_id: int):
        notification = self.get(db, notification_id)
        if notification:
            db.delete(notification)
            db.commit()
        return notification

notification_crud = NotificationCRUD()
