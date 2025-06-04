from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.notification_schema import NotificationCreate, NotificationOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.notification_crud import notification_crud

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=APIResponse[NotificationOut])
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    created = notification_crud.create(db, notification)
    return success_response(created, "Notification created successfully")

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
