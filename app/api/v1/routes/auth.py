# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.core.decorators import standardize_response  # Fixed import
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserAll, UserCreate
from app.schemas.auth_schema import LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=APIResponse[UserAll])
@standardize_response
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate):
    user_exists = user_crud.get_by_email(db, email=user_in.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = user_crud.create_user(db=db, obj_in=user_in)
    print(user_dict)
    return success_response(
        data=user,
        message="User created successfully",
        status_code=201
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
@standardize_response
def login_user(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token(user.email)
    response_data = LoginResponse(access_token=token, token_type="bearer", user=user)
    return success_response(
        data=response_data,
        status_code=200,
        message="Login successful"
    )
