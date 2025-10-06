from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from app.database.session import get_db
from app.crud.user_crud import user_crud
from app.services.firebase_service import firebase_notification_service
from app.utils.notification_helper import send_notification
from app.models.user import User
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()

@router.post("/test-firebase-direct/{user_id}")
def test_firebase_direct(
    user_id: int,
    title: str = "Test Notification",
    body: str = "This is a test notification",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test Firebase notification service directly
    """
    print(f"🔥 TESTING: Direct Firebase notification to user {user_id}")
    
    # Get target user
    target_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not target_user:
        print(f"❌ ERROR: User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ User found: {target_user.username}")
    print(f"📱 FCM Token: {target_user.fcm_token[:20] if target_user.fcm_token else 'None'}...")
    
    if not target_user.fcm_token:
        print(f"❌ ERROR: User {user_id} has no FCM token")
        raise HTTPException(status_code=400, detail="User has no FCM token")
    
    # Test Firebase service directly
    print(f"🚀 Sending notification via Firebase...")
    result = firebase_notification_service.send_notification(
        token=target_user.fcm_token,
        title=title,
        body=body,
        data={
            "test": "true",
            "user_id": str(user_id),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )
    
    print(f"📊 Firebase result: {result}")
    
    return {
        "success": True,
        "target_user": {
            "id": target_user.id,
            "username": target_user.username,
            "has_fcm_token": bool(target_user.fcm_token)
        },
        "firebase_result": result,
        "message": "Direct Firebase test completed"
    }

@router.post("/test-notification-helper/{user_id}")
def test_notification_helper(
    user_id: int,
    title: str = "Test Helper Notification",
    body: str = "This is a test notification via helper",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test notification helper function (includes DB save)
    """
    print(f"🛠️ TESTING: Notification helper to user {user_id}")
    
    # Get target user
    target_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not target_user:
        print(f"❌ ERROR: User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ User found: {target_user.username}")
    
    try:
        # Test notification helper
        print(f"🚀 Sending notification via helper...")
        notification = send_notification(
            db=db,
            title=title,
            body=body,
            type="test",
            target_user=target_user,
            sender=current_user
        )
        
        print(f"✅ Notification created with ID: {notification.id}")
        
        return {
            "success": True,
            "notification": {
                "id": notification.id,
                "title": notification.title,
                "body": notification.body,
                "created_at": notification.created_at.isoformat()
            },
            "target_user": {
                "id": target_user.id,
                "username": target_user.username,
                "has_fcm_token": bool(target_user.fcm_token)
            },
            "message": "Notification helper test completed"
        }
        
    except Exception as e:
        print(f"❌ ERROR in notification helper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Notification helper failed: {str(e)}")

@router.get("/firebase-status")
def check_firebase_status():
    """
    Check Firebase service initialization status
    """
    print(f"🔍 CHECKING: Firebase service status")
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        import os
        
        # Check if Firebase is initialized
        try:
            app = firebase_admin.get_app()
            firebase_initialized = True
            print(f"✅ Firebase app initialized: {app.name}")
        except ValueError:
            firebase_initialized = False
            print(f"❌ Firebase app not initialized")
        
        # Check service account key file
        cred_path = os.path.join(os.getcwd(), "wellness_service_account_key.json")
        key_file_exists = os.path.exists(cred_path)
        print(f"🔑 Service account key exists: {key_file_exists}")
        
        if key_file_exists:
            try:
                with open(cred_path, 'r') as f:
                    key_data = json.load(f)
                    project_id = key_data.get('project_id', 'Unknown')
                    print(f"📋 Project ID: {project_id}")
            except Exception as e:
                project_id = f"Error reading: {str(e)}"
                print(f"❌ Error reading key file: {str(e)}")
        else:
            project_id = "Key file not found"
        
        return {
            "firebase_initialized": firebase_initialized,
            "service_account_key_exists": key_file_exists,
            "service_account_path": cred_path,
            "project_id": project_id,
            "message": "Firebase status check completed"
        }
        
    except Exception as e:
        print(f"❌ ERROR checking Firebase status: {str(e)}")
        return {
            "error": str(e),
            "message": "Firebase status check failed"
        }

@router.get("/users-with-fcm-tokens")
def get_users_with_fcm_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of users with FCM tokens for testing
    """
    print(f"👥 CHECKING: Users with FCM tokens")
    
    try:
        # Get users with FCM tokens
        users = db.query(User).filter(User.fcm_token.isnot(None)).all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "fcm_token_preview": user.fcm_token[:20] + "..." if user.fcm_token else None,
                "has_fcm_token": bool(user.fcm_token)
            })
        
        print(f"📊 Found {len(user_list)} users with FCM tokens")
        
        return {
            "total_users_with_tokens": len(user_list),
            "users": user_list,
            "message": "Users with FCM tokens retrieved"
        }
        
    except Exception as e:
        print(f"❌ ERROR getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.post("/simulate-chat-notification/{room_id}")
def simulate_chat_notification(
    room_id: int,
    message_content: str = "Test chat message",
    message_type: str = "text",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulate the chat notification flow without WebSocket
    """
    print(f"💬 TESTING: Chat notification simulation for room {room_id}")
    
    try:
        from app.core.websocket_manager import manager
        
        # Test the notification method directly
        print(f"🚀 Calling send_notifications_to_other_users...")
        manager.send_notifications_to_other_users(
            db=db,
            room_id=room_id,
            sender=current_user,
            message_type=message_type,
            message_content=message_content
        )
        
        return {
            "success": True,
            "room_id": room_id,
            "sender": {
                "id": current_user.id,
                "username": current_user.username
            },
            "message_type": message_type,
            "message_content": message_content,
            "message": "Chat notification simulation completed"
        }
        
    except Exception as e:
        print(f"❌ ERROR in chat notification simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat notification simulation failed: {str(e)}")
