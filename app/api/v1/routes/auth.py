from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.crud.user_crud import user_crud
from app.crud.referral_crud import referral_crud
from app.crud.reward_crud import reward_crud
from app.database.session import get_db
from app.core.decorators import standardize_response  
from app.models.user import User, UserRole
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserAll, UserCreate, UserLogin,UserRead
from app.schemas.auth_schema import LoginResponse, AdminLogin,AdminLoginResponse
# from app.utils.firebase_auth import verify_firebase_token
from app.core.settings import settings
from app.dependencies.auth_dependency import get_current_user
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=APIResponse[LoginResponse])
@standardize_response
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate):
    user_exists = user_crud.get_by_phone(db, phone_number=user_in.phone_number)
    if user_exists:
        raise HTTPException(status_code=400, detail="Phone Number already exists")
    print(user_in.role)
    if user_in.role == UserRole.official:
        missing_fields = []
        if not user_in.sponsor_name:
            missing_fields.append("sponsor_name")
        if not user_in.sponsor_code:
            missing_fields.append("sponsor_code")
        if not user_in.distributor_code:
            missing_fields.append("distributor_code")

        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields for OFFICIAL role: {', '.join(missing_fields)}"
            )
    
    # Create the user first
    user = user_crud.create_user(db=db, obj_in=user_in)
    
    # Process referral code if provided
    referral_message = ""
    if user_in.referral_code:
        referral_result = referral_crud.validate_and_process_referral(
            db=db,
            referral_code=user_in.referral_code,
            new_user_id=user.id
        )
        
        if referral_result["success"]:
            # Create rewards for both users
            reward_result = reward_crud.process_referral_rewards(
                db=db,
                referrer_id=referral_result["referrer"].id,
                referred_user_id=user.id,
                referral_id=referral_result["referral_relationship"].id
            )
            
            if reward_result["success"]:
                referral_message = f" Referral bonus applied! You received 30 days of discount."
            else:
                referral_message = f" Referral processed but rewards failed: {reward_result['message']}"
        else:
            referral_message = f" Referral code issue: {referral_result['message']}"
    
    token = create_access_token(user.id)
    success_message = f"User created successfully{referral_message}"
    
    return success_response(
        data=LoginResponse(access_token=token, token_type="bearer", user=user),
        message=success_message,
        status_code=201
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
@standardize_response
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.get_by_phone(db, phone_number=user_in.phone_number,is_deleted=False)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect phone number")
    
    token = create_access_token(user.id)
    response_data = LoginResponse(access_token=token, token_type="bearer", user=user)
    return success_response(
        data=response_data,
        status_code=200,
        message="Login successful"
    )

@router.post("/admin/login", response_model=APIResponse[AdminLoginResponse])
@standardize_response
def admin_login(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    print("Admin login attempt with username:", form_data.username)
    admin = user_crud.authenticate_admin(db, username=form_data.username, password=form_data.password)
    if not admin:
        print("Admin authentication failed")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print("Admin authenticated successfully. ID:", admin.id, "Role:", admin.role)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(admin.id, expires_delta=access_token_expires)
    print("Created access token:", access_token)
    response_data = AdminLoginResponse(access_token=access_token, token_type="bearer", user=admin)
    return success_response(
        data=response_data,
        status_code=200,
        message="Login successful"
    )

@router.get("/me",response_model=APIResponse[UserRead])
@standardize_response
def my_profile(*, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success_response(data=UserRead.model_validate(current_user),message="User fetched successfully")

