from fastapi import APIRouter, Depends,HTTPException

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions, get_current_user
from app.models.user import UserRole, User
from app.crud.user_crud import user_crud
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.api_response import success_response, APIResponse
from app.schemas.user_schema import UserCreate, UserRead, UserAll, FCMTokenUpdate, UserUpdate,UpdateProfilePictureRequest
router = APIRouter(prefix="/users")


@router.get("/", response_model=APIResponse[list[UserAll]])
@standardize_response
def get_users(db: Session = Depends(get_db),
              current_user: User = Depends(check_user_permissions(UserRole.admin))):
    users = user_crud.get_all_users(db=db)
    safe_users = [UserAll.model_validate(user) for user in users]
    return success_response(data=safe_users, message="Users fetched successfully")


@router.get("/{user_id}", response_model=APIResponse[UserRead])
@standardize_response
def get_user(user_id: int, db: Session = Depends(get_db),
             ):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        return success_response(message="User not found")
    return success_response(
        data=UserRead.model_validate(user),
        message="User fetched successfully"
    )

@router.delete("/{user_id}")
def del_user(user_id: int, db: Session = Depends(get_db),
             admin_check: User = Depends(check_user_permissions(UserRole.admin,UserRole.user))):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        return success_response(message="User not found")
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return success_response(message="User deleted successfully")

@router.put("/fcm-token/{user_id}", response_model=APIResponse[UserRead])
@standardize_response
def update_fcm_token(user_id: int, token_data: FCMTokenUpdate, db: Session = Depends(get_db)):
    user = user_crud.update_fcm_token(db=db, user_id=user_id, fcm_token=token_data.fcm_token)
    return success_response(
        data=user,
        message="FCM token updated successfully"
    )


@router.post("/", response_model=APIResponse[UserRead])
@standardize_response
def create_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    # Check if user with phone number already exists
    existing_user = user_crud.get_by_phone(db=db, phone_number=user_data.phone_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this phone number already exists")
    
    user = user_crud.create_user(db=db, obj_in=user_data)
    return success_response(
        data=UserRead.model_validate(user),
        message="User created successfully"
    )


@router.put("/{user_id}", response_model=APIResponse[UserRead])
@standardize_response
def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    user = user_crud.update_user(db=db, user_id=user_id, obj_in=user_data)
    return success_response(
        data=user,
        message="User updated successfully"
    )

@router.put("/me/profile-pic", response_model=APIResponse[UserRead])
@standardize_response
def update_user_image(request: UpdateProfilePictureRequest, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    current_user.image_url = request.image_url
    db.commit()
    db.refresh(current_user)
    return success_response(
        data=current_user,
        message="Profile picture updated successfully"
    )