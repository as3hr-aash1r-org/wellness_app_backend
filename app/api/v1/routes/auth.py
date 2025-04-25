from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.schemas.user_schema import User, UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=User)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate):
    user_exists = user_crud.get_by_email(db, email=user_in.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = user_crud.create_user(db=db, obj_in=user_in)
    return user


@router.post("/login")
def login_user(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    token = create_access_token(user.email)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    user_role = user_crud.get_by_email(db=db, email=user.email)
    return {"access_token": token, "token_type": "bearer", "role": user_role.role, "user_id": user_role.id}
