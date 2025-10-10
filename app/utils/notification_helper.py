# app/services/notification_service.py

from app.schemas.notification_schema import NotificationCreate
from app.crud.notification_crud import notification_crud
from app.models.user import User
from app.services.firebase_service import firebase_notification_service
import json
from sqlalchemy.orm import Session


def send_notification(
    db: Session,
    title: str,
    body: str,
    type: str,
    target_user: User,
    sender: User
):
    
    if not target_user:
        raise ValueError("Target user not found")

    if not target_user.fcm_token:
        raise ValueError("Target user has no FCM token")
    

    # Save to DB
    notification_in = NotificationCreate(
        title=title,
        body=body,
        type=type,
        target_user_id=target_user.id,
        sender_id=sender.id
    )
    notification = notification_crud.create(db, notification_in)

    user_info = {
        "id": str(sender.id),
        "username": sender.username,
        "image_url": sender.image_url or ""
    }


    firebase_result = firebase_notification_service.send_notification(
        token=target_user.fcm_token,
        title=title,
        body=body,
        data={
            "title": notification.title,
            "body": notification.body,
            "type": notification.type,
            "id": str(notification.id),
            "created_at": notification.created_at.isoformat(),
            "target_user_id": str(notification.target_user_id),
            "user": json.dumps(user_info)
        }
    )
    
    

    return notification
