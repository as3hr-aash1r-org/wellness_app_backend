from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.core.settings import settings
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
 
    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        phone_number: str = payload.get("sub") 
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_by_phone(db=db, phone_number=phone_number) 
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def check_user_permissions(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return role_checker
