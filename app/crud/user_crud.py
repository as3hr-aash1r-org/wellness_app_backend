from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_hashed_password, verify_password
from app.models.user import User,UserRole
from app.schemas.auth_schema import AdminLogin
from app.schemas.user_schema import UserCreate
from app.utils.country_helper import get_country_details


class CRUDUser:
    def create_user(self, db: Session, *, obj_in: UserCreate):
        country, country_code = get_country_details(obj_in.phone_number)

        db_obj = User(
            username = obj_in.username,
            phone_number=obj_in.phone_number,
            role=obj_in.role,
            sponsor_name=obj_in.sponsor_name,
            sponsor_code=obj_in.sponsor_code,
            distributor_code=obj_in.distributor_code,
            country=country,
            country_code=country_code
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate_user(self, db: Session, *, phone_number: str):
        user = self.get_by_phone(db, phone_number=phone_number)
        if not user:
            return None
        # if not verify_password(password, user.password_hash):
        #     return None
        return user

    def create_admin(self,db: Session, obj_in: AdminLogin):
        db_obj = User(
            email=obj_in.email,
            password_hash=get_hashed_password(obj_in.password),
            role=UserRole.admin
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate_admin(self,db: Session, username: str, password: str):
        print("Authenticating admin with email:", username)
        user = self.get_by_email(db, email=username)
        print("User found by email:", user is not None)
        if not user:
            print("No user found with this email")
            return None
        print("User role:", user.role)
        print("Verifying password")
        if not verify_password(password, user.password_hash):
            print("Password verification failed")
            return None
        if user.role != UserRole.admin:
            print("User is not an admin")
            return None
        print("Admin authentication successful")
        return user

    def get_by_email(self, db: Session, *, email: str):
        query = select(User).where(User.email == email)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_by_phone(self, db: Session, *, phone_number: str):
        query = select(User).where(User.phone_number == phone_number)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_user_by_id(self, db: Session, *, user_id: int):
        query = select(User).where(User.id == user_id)
        result = db.execute(query)
        # print(result)
        return result.scalar_one_or_none()

    def get_all_users(self, db: Session):
        query = select(User).order_by(User.id)
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

    def update_fcm_token(self, db: Session, *, user_id: int, fcm_token: str):
        user = self.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(400, "User not found")
        user.fcm_token = fcm_token
        db.commit()
        return user
        
    def update_user(self, db: Session, *, user_id: int, obj_in):
        user = self.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
                
        db.commit()
        db.refresh(user)
        return user

    

user_crud = CRUDUser()
