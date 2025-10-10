from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.notification_schema import NotificationCreate, NotificationOut, BroadcastNotificationRequest
from app.schemas.api_response import success_response, APIResponse
from app.crud.notification_crud import notification_crud
from app.models.user import User, UserRole
from app.dependencies.auth_dependency import get_current_user
from app.utils.notification_helper import send_notification
from app.services.firebase_service import firebase_notification_service
from app.crud.user_crud import user_crud
from typing import Optional
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

@router.post("/broadcast", response_model=APIResponse[dict])
def broadcast_notification(
    request: BroadcastNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast notification to all users (admin only)
    Optional role_filter: "user" or "expert" to target specific roles
    """
    # Check if user is admin
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can send broadcast notifications")
    
    print(f"📢 BROADCAST: Admin {current_user.username or current_user.id} sending broadcast notification")
    print(f"📝 Title: {request.title}")
    print(f"📄 Body: {request.body}")
    print(f"🎯 Role Filter: {request.role_filter or 'All users'}")
    
    try:
        # Get all users
        all_users = user_crud.get_all_users(db)
        
        # Filter users based on role_filter
        if request.role_filter:
            if request.role_filter.lower() == "user":
                target_users = [user for user in all_users if user.role == UserRole.user]
            elif request.role_filter.lower() == "expert":
                target_users = [user for user in all_users if user.role == UserRole.expert]
            else:
                raise HTTPException(status_code=400, detail="Invalid role_filter. Use 'user' or 'expert'")
        else:
            # All users except admins
            target_users = [user for user in all_users if user.role != UserRole.admin]
        
        # Filter users with FCM tokens
        users_with_tokens = [user for user in target_users if user.fcm_token]
        fcm_tokens = [user.fcm_token for user in users_with_tokens]
        
        print(f"📊 Total target users: {len(target_users)}")
        print(f"📱 Users with FCM tokens: {len(users_with_tokens)}")
        
        if not fcm_tokens:
            return success_response(
                {
                    "notifications_sent": 0,
                    "total_target_users": len(target_users),
                    "users_with_tokens": 0,
                    "role_filter": request.role_filter
                },
                "No users with FCM tokens found"
            )
        
        # Save notifications to database for each user
        saved_count = 0
        for user in users_with_tokens:
            try:
                from app.schemas.notification_schema import NotificationCreate
                notification_in = NotificationCreate(
                    title=request.title,
                    body=request.body,
                    type="broadcast",
                    target_user_id=user.id,
                    sender_id=current_user.id
                )
                notification_crud.create(db, notification_in)
                saved_count += 1
            except Exception as e:
                print(f"❌ Failed to save notification for user {user.id}: {e}")
        
        # Send multicast notification via Firebase (using optimized method)
        print(f"🚀 Sending multicast notification to {len(fcm_tokens)} devices...")
        
        # Prepare data for Firebase
        notification_data = {
            "type": "broadcast",
            "sender_id": str(current_user.id),
            "sender_username": str(current_user.username or f"User_{current_user.id}"),
            "role_filter": str(request.role_filter or "all")
        }
        
        print(f"🔍 BROADCAST: Prepared data: {notification_data}")
        
        # Send multicast notification
        firebase_result = firebase_notification_service.send_multicast_notification(
            tokens=fcm_tokens,
            title=request.title,
            body=request.body,
            data=notification_data
        )
        
        # Clean up invalid tokens if any failed
        if firebase_result.get("failure_count", 0) > 0 and firebase_result.get("responses"):
            invalid_tokens = []
            for i, response in enumerate(firebase_result["responses"]):
                if not response.success and "not found" in str(response.exception).lower():
                    invalid_token = fcm_tokens[i]
                    invalid_tokens.append(invalid_token)
                    print(f"🧹 CLEANUP: Marking token {invalid_token[:10]}... as invalid")
            
            # Remove invalid tokens from database
            if invalid_tokens:
                try:
                    from sqlalchemy import update
                    stmt = update(User).where(User.fcm_token.in_(invalid_tokens)).values(fcm_token=None)
                    db.execute(stmt)
                    db.commit()
                    print(f"🧹 CLEANUP: Removed {len(invalid_tokens)} invalid tokens from database")
                except Exception as e:
                    print(f"❌ CLEANUP ERROR: {str(e)}")
        
        print(f"📊 Firebase result: {firebase_result}")
        
        result = {
            "notifications_sent": firebase_result.get("success_count", 0),
            "notifications_failed": firebase_result.get("failure_count", 0),
            "total_target_users": len(target_users),
            "users_with_tokens": len(users_with_tokens),
            "saved_to_database": saved_count,
            "role_filter": request.role_filter,
            "firebase_success": firebase_result.get("success", False)
        }
        
        if firebase_result.get("success"):
            message = f"Broadcast sent successfully to {result['notifications_sent']} users"
            print(f"✅ {message}")
        else:
            message = f"Broadcast failed: {firebase_result.get('error', 'Unknown error')}"
            print(f"❌ {message}")
        
        return success_response(result, message)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        print(f"❌ BROADCAST ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")
