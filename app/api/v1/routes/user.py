from fastapi import APIRouter, Depends

from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions, get_current_user
from app.models.user import UserRole, User
from app.crud.user_crud import user_crud
from sqlalchemy.orm import Session

from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserAll

router = APIRouter(prefix="/users")


@router.get("/", response_model=APIResponse[list[UserAll]])
def get_users(db: Session = Depends(get_db),
              current_user: User = Depends(check_user_permissions(UserRole.ADMIN))):
    users = user_crud.get_all_users(db=db)
    return success_response(data=users, message="Users fetched successfully")


@router.delete("/{user_id}")
def del_user(user_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(check_user_permissions(UserRole.ADMIN))):
    user = user_crud.delete_user(db=db, user_id=user_id)
    db.delete(user)
    db.commit()
    return success_response(message="User deleted successfully")
