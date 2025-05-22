from fastapi import APIRouter, Depends

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions, get_current_user
from app.models.user import UserRole, User
from app.crud.user_crud import user_crud
from sqlalchemy.orm import Session

from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserCreate, UserRead, UserAll, FCMTokenUpdate

router = APIRouter(prefix="/users")


@router.get("/", response_model=APIResponse[list[UserAll]])
@standardize_response
def get_users(db: Session = Depends(get_db),
              current_user: User = Depends(check_user_permissions(UserRole.admin))):
    users = user_crud.get_all_users(db=db)
    safe_users = [UserAll.model_validate(user) for user in users]
    return success_response(data=safe_users, message="Users fetched successfully")


@router.get("/{user_id}", response_model=APIResponse[UserAll])
@standardize_response
def get_user(user_id: int, db: Session = Depends(get_db),
             ):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        return success_response(message="User not found")
    return success_response(
        data=user,
        message="User fetched successfully"
    )

@router.delete("/{user_id}")
def del_user(user_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(check_user_permissions(UserRole.admin))):
    user = user_crud.delete_user(db=db, user_id=user_id)
    db.delete(user)
    db.commit()
    return success_response(message="User deleted successfully")

@router.put("/fcm-token/{user_id}", response_model=APIResponse[UserRead])
@standardize_response
def update_fcm_token(user_id: int, token_data: FCMTokenUpdate, db: Session = Depends(get_db)):
    user = user_crud.update_fcm_token(db=db, user_id=user_id, fcm_token=token_data.fcm_token)
    return success_response(
        data=user,
        message="FCM token updated successfully"
    )
