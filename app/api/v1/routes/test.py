from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.decorators import standardize_response
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user, check_user_permissions
from app.models.user import User, UserRole
from app.crud.user_crud import user_crud
from app.crud.chat_crud import chat_room_crud
from app.schemas.api_response import success_response, APIResponse
from app.services.firebase_service import firebase_notification_service

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/notification/{user_id}", response_model=APIResponse[dict])
@standardize_response
def test_notification(
    user_id: int = Path(...),
    message: str = Query("This is a test notification"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Test sending a notification to a specific user (admin only)"""
    # Get the target user
    target_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not target_user:
        return success_response(
            message="User not found",
            status_code=404
        )
    
    # Check if the user has an FCM token
    if not hasattr(target_user, 'fcm_token') or not target_user.fcm_token:
        return success_response(
            message="User does not have an FCM token",
            status_code=400
        )
    
    # Send the notification
    result = firebase_notification_service.send_notification(
        token=target_user.fcm_token,
        title=f"Test from {current_user.username}",
        body=message,
        data={
            "notification_type": "test",
            "sender_id": str(current_user.id)
        }
    )
    
    return success_response(
        data=result,
        message="Notification sent"
    )


@router.get("/notification/room/{room_id}", response_model=APIResponse[dict])
@standardize_response
def test_room_notification(
    room_id: int = Path(...),
    message: str = Query("New message in chat room"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(check_user_permissions())
):
    """Test sending a notification to all users in a chat room (admin only)"""
    # Get the chat room
    chat_room = chat_room_crud.get_chat_room(db, room_id=room_id)
    if not chat_room:
        return success_response(
            message="Chat room not found",
            status_code=404
        )
    
    # Get all users in the chat room
    users = chat_room_crud.get_chat_room_users(db, room_id=room_id)
    if not users:
        return success_response(
            message="No users found in chat room",
            status_code=404
        )
    
    # Collect FCM tokens
    fcm_tokens = []
    for user in users:
        if hasattr(user, 'fcm_token') and user.fcm_token:
            fcm_tokens.append(user.fcm_token)
    
    if not fcm_tokens:
        return success_response(
            message="No users with FCM tokens found",
            status_code=400
        )
    
    # Send the notification
    result = firebase_notification_service.send_multicast_notification(
        tokens=fcm_tokens,
        title=f"Test from {current_user.username}",
        body=message,
        data={
            "notification_type": "test",
            "room_id": str(room_id),
            "sender_id": str(current_user.id)
        }
    )
    
    return success_response(
        data=result,
        message="Notifications sent"
    )


@router.get("/debug/fcm-tokens", response_model=APIResponse[list])
@standardize_response
def debug_fcm_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    """Debug endpoint to list all users with FCM tokens (admin only)"""
    # Get all users
    users = user_crud.get_all_users(db)
    
    # Filter users with FCM tokens
    users_with_tokens = []
    for user in users:
        if hasattr(user, 'fcm_token') and user.fcm_token:
            users_with_tokens.append({
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "fcm_token": user.fcm_token[:20] + "..." if len(user.fcm_token) > 20 else user.fcm_token
            })
    
    return success_response(
        data=users_with_tokens,
        message=f"Found {len(users_with_tokens)} users with FCM tokens"
    )
