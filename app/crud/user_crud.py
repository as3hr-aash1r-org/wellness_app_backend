from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import get_hashed_password, verify_password
from app.models.user import User,UserRole
from app.models.referrals import Referrals
from app.schemas.auth_schema import AdminLogin
from app.schemas.user_schema import UserCreate, ExpertCreate, ExpertUpdate, ProfileUpdateRequest
from app.utils.referral_code_generator import generate_referral_code
from app.utils.country_utils import CountryValidator
from app.utils.id_generator import generate_user_ids

class CRUDUser:
    def create_user(self, db: Session, *, obj_in: UserCreate):
        from app.models.user import AppLevel
        
        # Use country and country_code provided by frontend
        country = obj_in.country.strip() if obj_in.country else "Unknown"
        country_code = obj_in.country_code.strip() if obj_in.country_code else "XX"
        
        # Clean and validate country data from frontend
        # Generate unique referral code using the strict 2-letter country code
        user_referral_code = generate_referral_code(db, country_code)
        
        # Generate user IDs based on role
        user_ids = generate_user_ids(db, obj_in.role.value)
        
        db_obj = User(
            username = obj_in.username,
            phone_number=obj_in.phone_number,
            role=obj_in.role,
            app_level=AppLevel.new_joiner,  # Set default level
            sponsor_name=obj_in.sponsor_name,
            sponsor_code=obj_in.sponsor_code,
            distributor_code=obj_in.distributor_code,
            country=country,
            country_code=country_code,
            referral_code=user_referral_code,
            g_id=user_ids["g_id"],
            d_id=user_ids["d_id"],
            i_id=user_ids["i_id"],
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
    def get_all_users(self, db: Session, skip: int = 0, limit: int = 100):
        query = select(User).order_by(User.id).offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def count_all_users(self, db: Session):
        from sqlalchemy import func
        query = select(func.count(User.id))
        result = db.execute(query)
        return result.scalar()
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
    
    def _handle_role_change_chat_rooms(self, db: Session, user: User, old_role: UserRole, new_role: UserRole):
        """Handle chat room implications when a user's role changes"""
        from app.models.chat import ChatRoom
        
        # Case 1: Expert → User/Official/Influencer
        if old_role == UserRole.expert and new_role in [UserRole.user, UserRole.official, UserRole.influencer]:
            # Check if there are other active experts
            other_experts_query = select(User).where(
                User.role == UserRole.expert,
                User.id != user.id,
                (User.is_deleted == False) | (User.is_deleted == None)
            )
            other_experts = list(db.execute(other_experts_query).scalars().all())
            
            if not other_experts:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot change role: This is the only expert in the system. At least one expert must remain."
                )
            
            # Find all active chat rooms where this user is the expert
            expert_rooms_query = select(ChatRoom).where(
                ChatRoom.expert_id == user.id,
                ChatRoom.is_active == True
            )
            expert_rooms = list(db.execute(expert_rooms_query).scalars().all())
            
            if expert_rooms:
                # Find the least busy expert from the available experts
                from app.crud.chat_crud import chat_room_crud
                least_busy_expert = chat_room_crud.find_least_busy_expert(db)
                
                if least_busy_expert:
                    # Reassign all chat rooms to the least busy expert
                    for room in expert_rooms:
                        room.expert_id = least_busy_expert.id
                        room.updated_at = datetime.utcnow()
                    print(f"Reassigned {len(expert_rooms)} chat rooms from expert {user.id} to expert {least_busy_expert.id}")
        
        # Case 2: User/Official/Influencer → Expert
        elif old_role in [UserRole.user, UserRole.official, UserRole.influencer] and new_role == UserRole.expert:
            # Find all active chat rooms where this user is the customer
            customer_rooms_query = select(ChatRoom).where(
                ChatRoom.user_id == user.id,
                ChatRoom.is_active == True
            )
            customer_rooms = list(db.execute(customer_rooms_query).scalars().all())
            
            if customer_rooms:
                # Soft delete (deactivate) all their customer chat rooms
                for room in customer_rooms:
                    room.is_active = False
                    room.updated_at = datetime.utcnow()
                print(f"Deactivated {len(customer_rooms)} chat rooms for user {user.id} (became expert)")
        
        # Case 3: User/Official/Influencer ↔ User/Official/Influencer or Admin changes
        # No action needed - chat rooms remain as-is
        
    def update_user(self, db: Session, *, user_id: int, obj_in):
        user = self.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Check if role is being updated
        role_changed = False
        old_role = user.role
        new_role = None
        if "role" in update_data and update_data["role"] != user.role:
            role_changed = True
            new_role = update_data["role"]
            
            # Handle chat room implications of role changes
            self._handle_role_change_chat_rooms(db, user, old_role, new_role)
        
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        # Generate additional IDs if role changed
        if role_changed:
            # Generate d_id if changed to official and doesn't have one
            if new_role == UserRole.official and not user.d_id:
                from app.utils.id_generator import UserIDGenerator
                user.d_id = UserIDGenerator.generate_d_id(db)
            
            # Generate i_id if changed to influencer and doesn't have one
            if new_role == UserRole.influencer and not user.i_id:
                from app.utils.id_generator import UserIDGenerator
                user.i_id = UserIDGenerator.generate_i_id(db)
                
        db.commit()
        db.refresh(user)
        return user

    def update_profile(self, db: Session, *, user_id: int, obj_in: ProfileUpdateRequest):
        """Update user profile with only editable fields"""
        user = self.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if codes are already set (locked)
        if user.sponsor_code and user.distributor_code:
            # Reject any attempt to update sponsor_code or distributor_code
            if obj_in.sponsor_code is not None or obj_in.distributor_code is not None:
                raise HTTPException(
                    status_code=400, 
                    detail="Sponsor and distributor codes are already locked and cannot be changed"
                )
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Check if both codes are being set for the first time
        codes_being_set = (
            'sponsor_code' in update_data and update_data['sponsor_code'] and
            'distributor_code' in update_data and update_data['distributor_code'] and
            not (user.sponsor_code and user.distributor_code)
        )
        
        # Only update allowed fields
        allowed_fields = {
            'username', 'sponsor_name', 'distributor_code', 
            'sponsor_code', 'image_url','distributor_rank','member_name','sponsor_rank','email','gender'
        }
        
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        # Trigger DXN New upgrade if both codes were just set
        if codes_being_set:
            from app.services.level_service import LevelService
            level_service = LevelService(db)
            level_service.upgrade_to_dxn_new(user.id)
                
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
        
        # Use provided country or default values
        country = obj_in.country if obj_in.country else "Unknown"
        country_code = "+000"  # Default for experts, can be updated later
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
            country=country,
            country_code=country_code,
            dxn_distributor_number=obj_in.dxn_distributor_number,
            role=UserRole.expert
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def get_all_experts(self, db: Session, skip: int = 0, limit: int = 100):
        query = select(User).where(User.role == UserRole.expert).order_by(User.id).offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def count_all_experts(self, db: Session):
        from sqlalchemy import func
        query = select(func.count(User.id)).where(User.role == UserRole.expert)
        result = db.execute(query)
        return result.scalar()
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
    
    def get_referrer_for_user(self, db: Session, *, user_id: int):
        """Get the referrer (person who referred this user) if exists"""
        query = (
            select(User)
            .join(Referrals, Referrals.referrer_user_id == User.id)
            .where(Referrals.referred_user_id == user_id)
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

user_crud = CRUDUser()