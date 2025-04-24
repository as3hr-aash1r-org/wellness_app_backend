from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.schemas.user_schema import User, UserCreate

router = APIRouter(prefix="/api", tags=["Auth"])


@router.post("/register", response_model=User)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate):
    user_exists = user_crud.get_by_email(db, email=user_in.email)
    if user_exists:
        return HTTPException(status_code=400, detail="Email already exists")
    user = user_crud.create_user(db=db, obj_in=user_in)
    return user
