from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.core.decorators import standardize_response  
from app.models.user import User, UserRole
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserAll, UserCreate, UserLogin
from app.schemas.auth_schema import LoginResponse, AdminLogin,AdminLoginResponse
# from app.utils.firebase_auth import verify_firebase_token


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
            
    user = user_crud.create_user(db=db, obj_in=user_in)
    token = create_access_token(user.phone_number)
    return success_response(
        data=LoginResponse(access_token=token, token_type="bearer", user=user),
        message="User created successfully",
        status_code=201
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
@standardize_response
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.authenticate_user(db, phone_number=user_in.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect phone number")
    
    token = create_access_token(user.phone_number)
    response_data = LoginResponse(access_token=token, token_type="bearer", user=user)
    return success_response(
        data=response_data,
        status_code=200,
        message="Login successful"
    )

@router.post("/admin/login", response_model=APIResponse[AdminLoginResponse])
@standardize_response
def admin_login(admin_in: AdminLogin, db: Session = Depends(get_db)):
    admin = user_crud.authenticate_admin(db, username=admin_in.email, password=admin_in.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(admin.email)
    response_data = AdminLoginResponse(access_token=token, token_type="bearer", user=admin)
    return success_response(
        data=response_data,
        status_code=200,
        message="Login successful"
    )



# @router.post("/register",response_model=APIResponse[LoginResponse])
# @standardize_response
# def firebase_register(payload: FirebaseAuthRequest, db: Session = Depends(get_db)):
#     try:
#         user_info = verify_firebase_token(payload.id_token)
#         phone_number = user_info["phone_number"]
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid Firebase token")

#     db_user = db.query(User).filter_by(phone_number=phone_number).first()
#     if not db_user:
#         db_user = User(phone_number=phone_number,username=payload.username)
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)

#     access_token = create_access_token(db_user.phone_number)

#     return success_response(
#         data=LoginResponse(access_token=access_token, token_type="bearer", user=db_user),
#         status_code=200,
#         message="Signup successful"
#     )
