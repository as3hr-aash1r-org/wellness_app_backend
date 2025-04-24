from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_hashed_password
from app.models.user import User
from app.schemas.user_schema import UserCreate


class CRUDUser:
    def create_user(self, db: Session, *, obj_in: UserCreate):
        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            password_hash=get_hashed_password(obj_in.password),
            phone_number=obj_in.phone_number,
            role=obj_in.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str):
        query = select(User).where(User.email == email)
        result = db.execute(query)
        return result.scalar_one_or_none()


user_crud = CRUDUser()
