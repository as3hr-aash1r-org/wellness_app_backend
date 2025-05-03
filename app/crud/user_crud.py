from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_hashed_password, verify_password
from app.models.user import User
from app.schemas.user_schema import UserCreate


class CRUDUser:
    def create_user(self, db: Session, *, obj_in: UserCreate):
        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            password_hash=get_hashed_password(obj_in.password),
            phone_number=obj_in.phone_number,
            role=obj_in.role,
            sponsor_code=obj_in.sponsor_code,
            distributor_code=obj_in.distributor_code
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate_user(self, db: Session, *, email: str, password: str):
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_by_email(self, db: Session, *, email: str):
        query = select(User).where(User.email == email)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_user_by_id(self, db: Session, *, user_id: int):
        query = select(User).where(User.id == user_id)
        result = db.execute(query)
        # print(result)
        return result.scalar_one_or_none()

    def get_all_users(self, db: Session):
        query = select(User)
        result = db.execute(query)
        return result.scalars().all()

    def delete_user(self, db: Session, *, user_id: int):
        query = select(User).where(User.id == user_id)
        print(query)
        result = db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(400, "User not found")
        return user


user_crud = CRUDUser()
