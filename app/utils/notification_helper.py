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
    print(f"🔔 NOTIFICATION_HELPER: Starting notification process")
    print(f"📋 Target: {target_user.username} (ID: {target_user.id})")
    print(f"👤 Sender: {sender.username} (ID: {sender.id})")
    print(f"📝 Title: {title}")
    print(f"📄 Body: {body}")
    print(f"🏷️ Type: {type}")
    
    if not target_user:
        print(f"❌ NOTIFICATION_HELPER: Target user not found")
        raise ValueError("Target user not found")

    if not target_user.fcm_token:
        print(f"❌ NOTIFICATION_HELPER: Target user {target_user.id} has no FCM token")
        raise ValueError("Target user has no FCM token")
    
    print(f"📱 NOTIFICATION_HELPER: FCM Token exists: {target_user.fcm_token[:20]}...")

    # Save to DB
    print(f"💾 NOTIFICATION_HELPER: Saving notification to database...")
    notification_in = NotificationCreate(
        title=title,
        body=body,
        type=type,
        target_user_id=target_user.id,
        sender_id=sender.id
    )
    notification = notification_crud.create(db, notification_in)
    print(f"✅ NOTIFICATION_HELPER: Notification saved with ID: {notification.id}")

    user_info = {
        "id": str(sender.id),
        "username": sender.username,
        "image_url": sender.image_url or ""
    }

    print(f"🚀 NOTIFICATION_HELPER: Sending Firebase notification to user {target_user.id}")
    print(f"📱 NOTIFICATION_HELPER: Token: {target_user.fcm_token[:20]}...")

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
    
    print(f"📊 NOTIFICATION_HELPER: Firebase result: {firebase_result}")
    
    if firebase_result.get('success'):
        print(f"✅ NOTIFICATION_HELPER: Firebase notification sent successfully")
    else:
        print(f"❌ NOTIFICATION_HELPER: Firebase notification failed: {firebase_result.get('error')}")

    print(f"🎉 NOTIFICATION_HELPER: Notification process completed")
    return notification
