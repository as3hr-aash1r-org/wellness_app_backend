from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.crud.user_crud import user_crud
from app.crud.referral_crud import referral_crud
from app.crud.reward_crud import reward_crud
from app.crud.otp_crud import otp_crud
from app.database.session import get_db
from app.core.decorators import standardize_response
from app.models.user import User, UserRole
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserCreate, UserLogin, UserRead
from app.schemas.auth_schema import LoginResponse, AdminLoginResponse
from app.schemas.otp_schema import OTPRequest, OTPVerifyWithRegistration
from app.core.settings import settings
from app.dependencies.auth_dependency import get_current_user
from app.services.sms_service import sms_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-otp", response_model=APIResponse[dict])
@standardize_response
def request_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Request OTP for phone number verification (used for both register and login)"""
    # Check rate limiting
    rate_check = otp_crud.can_request_otp(db, otp_request.phone_number)
    if not rate_check["can_request"]:
        raise HTTPException(status_code=429, detail=rate_check["message"])
    
    # Create OTP record
    otp_record = otp_crud.create_otp(db, otp_request.phone_number)
    
    # Send OTP via SMS.to
    sms_result = sms_service.send_otp(otp_request.phone_number, otp_record.otp_code)
    
    if not sms_result["success"]:
        raise HTTPException(status_code=500, detail=sms_result["message"])
    
    return success_response(
        data={"message": "OTP sent successfully", "expires_in_minutes": 10},
        message="OTP sent to your phone number",
        status_code=200
    )


@router.post("/verify-otp", response_model=APIResponse[LoginResponse])
@standardize_response
def verify_otp_endpoint(
    request: OTPVerifyWithRegistration,
    db: Session = Depends(get_db)
):
    """Verify OTP and register/login user"""
    # Verify OTP
    verification_result = otp_crud.verify_otp(
        db,
        request.phone_number,
        request.otp_code
    )
    
    if not verification_result["success"]:
        raise HTTPException(status_code=400, detail=verification_result["message"])
    
    # Check if user exists (login) or create new user (register)
    user = user_crud.get_by_phone(db, phone_number=request.phone_number, is_deleted=False)
    
    if user:
        # Existing user - login
        token = create_access_token(user.id)
        return success_response(
            data=LoginResponse(access_token=token, token_type="bearer", user=user),
            message="Login successful",
            status_code=200
        )
    else:
        # New user - register
        if not request.user_data:
            raise HTTPException(
                status_code=400,
                detail="User registration data required for new users"
            )
        
        user_data = request.user_data
        
        # Validate phone number matches
        if user_data.phone_number != request.phone_number:
            raise HTTPException(
                status_code=400,
                detail="Phone number mismatch"
            )
        
        # Validate official role fields
        if user_data.role == UserRole.official:
            missing_fields = []
            if not user_data.sponsor_name:
                missing_fields.append("sponsor_name")
            if not user_data.sponsor_code:
                missing_fields.append("sponsor_code")
            if not user_data.distributor_code:
                missing_fields.append("distributor_code")
            
            if missing_fields:
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing required fields for OFFICIAL role: {', '.join(missing_fields)}"
                )
        
        # Create the user
        user = user_crud.create_user(db=db, obj_in=user_data)
        
        # Process referral code if provided
        referral_message = ""
        if user_data.referral_code:
            referral_result = referral_crud.validate_and_process_referral(
                db=db,
                referral_code=user_data.referral_code,
                new_user_id=user.id
            )
            
            if referral_result["success"]:
                reward_result = reward_crud.process_referral_rewards(
                    db=db,
                    referrer_id=referral_result["referrer"].id,
                    referred_user_id=user.id,
                    referral_id=referral_result["referral_relationship"].id
                )
                
                if reward_result["success"]:
                    referral_message = " Referral bonus: 30 days"
        
        token = create_access_token(user.id)
        success_message = f"User registered successfully{referral_message}"
        
        return success_response(
            data=LoginResponse(access_token=token, token_type="bearer", user=user),
            message=success_message,
            status_code=201
        )


@router.post("/register", response_model=APIResponse[LoginResponse])
@standardize_response
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate):
    print("Incoming request:", user_in.model_dump())
    user_exists = user_crud.get_by_phone(db, phone_number=user_in.phone_number)
    if user_exists:
        raise HTTPException(status_code=400, detail="Phone Number already exists")
    print("Incoming request",user_in)
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
                referral_message = "Referral bonus: 30 days"
            else:
                referral_message = None
        else:
            referral_message = None
    
    token = create_access_token(user.id)
    success_message = f"User created successfully {referral_message}"
    
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

