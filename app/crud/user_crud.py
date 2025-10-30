from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_hashed_password, verify_password
from app.models.user import User,UserRole
from app.schemas.auth_schema import AdminLogin
from app.schemas.user_schema import UserCreate, ExpertCreate, ExpertUpdate, ProfileUpdateRequest
from app.utils.country_helper import get_country_details
from app.utils.referral_code_generator import generate_referral_code


class CRUDUser:
    def create_user(self, db: Session, *, obj_in: UserCreate):
        country, country_code = get_country_details(obj_in.phone_number)

        # Generate unique referral code for the new user with country-specific prefix
        user_referral_code = generate_referral_code(db, country)
        
        db_obj = User(
            username = obj_in.username,
            phone_number=obj_in.phone_number,
            role=obj_in.role,
            sponsor_name=obj_in.sponsor_name,
            sponsor_code=obj_in.sponsor_code,
            distributor_code=obj_in.distributor_code,
            country=country,
            country_code=country_code,
            referral_code=user_referral_code
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

    def get_by_phone(self, db: Session, *, phone_number: str,is_deleted: bool = False):
        query = select(User).where(User.phone_number == phone_number)
        if not is_deleted:
            query = query.where(User.is_deleted == False)
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
    
    def update_profile(self, db: Session, *, user_id: int, obj_in: ProfileUpdateRequest):
        """Update user profile with only editable fields"""
        user = self.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Only update allowed fields
        allowed_fields = {
            'username', 'sponsor_name', 'distributor_code', 
            'sponsor_code', 'image_url','distributor_rank','member_name','sponsor_rank','email','gender'
        }
        
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
                
        db.commit()
        db.refresh(user)
        return user

    # Expert-specific CRUD operations
    def create_expert(self, db: Session, *, obj_in: ExpertCreate):
        # Check if phone number already exists
        existing_user = self.get_by_phone(db, phone_number=obj_in.phone_number)
        if existing_user:
            raise HTTPException(status_code=400, detail="Phone number already exists")
            
        # Check if email already exists (if provided)
        if obj_in.email:
            existing_email = self.get_by_email(db, email=obj_in.email)
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Get country details from phone number
        country, country_code = get_country_details(obj_in.phone_number)
        if not obj_in.country:  # Use detected country if not provided
            country = obj_in.country or country

        # Create the expert user
        db_obj = User(
            first_name=obj_in.first_name,
            middle_name=obj_in.middle_name,
            last_name=obj_in.last_name,
            username=f"{obj_in.first_name} {obj_in.last_name}",  # Generate username
            phone_number=obj_in.phone_number,
            email=obj_in.email,
            password_hash=get_hashed_password(obj_in.password),
            date_of_birth=obj_in.date_of_birth,
            gender=obj_in.gender,
            position=obj_in.position,
            country=obj_in.country or country,
            country_code=country_code,
            dxn_distributor_number=obj_in.dxn_distributor_number,
            role=UserRole.expert
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_all_experts(self, db: Session):
        query = select(User).where(User.role == UserRole.expert).order_by(User.id)
        result = db.execute(query)
        return result.scalars().all()

    def get_expert_by_id(self, db: Session, *, expert_id: int):
        query = select(User).where(User.id == expert_id, User.role == UserRole.expert)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def update_expert(self, db: Session, *, expert_id: int, obj_in: ExpertUpdate):
        expert = self.get_expert_by_id(db, expert_id=expert_id)
        if expert is None:
            raise HTTPException(status_code=404, detail="Expert not found")
            
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Check if phone number is being updated and if it already exists
        if "phone_number" in update_data and update_data["phone_number"]:
            existing_phone = self.get_by_phone(db, phone_number=update_data["phone_number"])
            if existing_phone and existing_phone.id != expert_id:
                raise HTTPException(status_code=400, detail="Phone number already exists")
        
        # Check if email is being updated and if it already exists
        if "email" in update_data and update_data["email"]:
            existing_email = self.get_by_email(db, email=update_data["email"])
            if existing_email and existing_email.id != expert_id:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Update username if first_name or last_name changed
        if "first_name" in update_data or "last_name" in update_data:
            first_name = update_data.get("first_name", expert.first_name)
            last_name = update_data.get("last_name", expert.last_name)
            update_data["username"] = f"{first_name} {last_name}"
        
        for field, value in update_data.items():
            if hasattr(expert, field) and value is not None:
                setattr(expert, field, value)
                
        db.commit()
        db.refresh(expert)
        return expert

    def delete_expert(self, db: Session, *, expert_id: int):
        expert = self.get_expert_by_id(db, expert_id=expert_id)
        if expert is None:
            raise HTTPException(status_code=404, detail="Expert not found")
        
        db.delete(expert)
        db.commit()
        return expert

user_crud = CRUDUser()
