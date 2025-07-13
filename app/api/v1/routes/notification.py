from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.notification_schema import NotificationCreate, NotificationOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.notification_crud import notification_crud
from app.models.user import User
from app.dependencies.auth_dependency import get_current_user
from app.utils.notification_helper import send_notification
import json

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# @router.post("/", response_model=APIResponse[NotificationOut])
# def create_notification(notification: NotificationCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
#     user = db.get(User, notification.target_user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if not user.fcm_token:
#         raise HTTPException(status_code=400, detail="User has no FCM token")
    
#     notification_data = notification.model_dump()
#     notification_data["sender_id"] = current_user.id
#     created = notification_crud.create(db, notification_data)
#     user_info = {
#         "id": str(current_user.id),
#         "username": current_user.username,
#         "image_url": current_user.image_url or ""
#     }
#     firebase_notification_service.send_notification(
#         token=user.fcm_token,
#         title=notification.title,
#         body=notification.body,
#         data={"title": created.title, 
#         "body": created.body, 
#         "type": created.type,
#         "id": str(created.id),
#         "created_at": created.created_at.isoformat(),
#         "target_user_id": str(created.target_user_id),
#         "sender":json.dumps(user_info)}
#     )

#     return success_response(created, "Notification sent successfully")



@router.post("/", response_model=APIResponse[NotificationOut])
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.get(User, notification.target_user_id)
    try:
        notification_obj = send_notification(
            db=db,
            title=notification.title,
            body=notification.body,
            type=notification.type,
            target_user=user,
            sender=current_user
        )
        return success_response(notification_obj, "Notification sent successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=APIResponse[list[NotificationOut]])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = notification_crud.get_all_for_user(db,current_user.id)
    return success_response(items, "Your notifications fetched successfully")


@router.get("/", response_model=APIResponse[list[NotificationOut]])
def get_all_notifications(db: Session = Depends(get_db)):
    items = notification_crud.get_all(db)
    return success_response(items, "Notifications fetched successfully")

@router.get("/{notification_id}", response_model=APIResponse[NotificationOut])
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    item = notification_crud.get(db, notification_id)
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")
    return success_response(item, "Notification fetched successfully")

@router.put("/{notification_id}", response_model=APIResponse[NotificationOut])
def update_notification(notification_id: int, notification: NotificationCreate, db: Session = Depends(get_db)):
    updated = notification_crud.update(db, notification_id, notification)
    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")
    return success_response(updated, "Notification updated successfully")

@router.delete("/{notification_id}", response_model=APIResponse[str])
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    deleted = notification_crud.delete(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return success_response("Notification deleted", "Notification deleted successfully")
