from typing import List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.decorators import standardize_response
from app.core.websocket_manager import manager
from app.crud.chat_crud import chat_room_crud, message_crud
from app.crud.user_crud import user_crud
from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user, check_user_permissions
from app.models.user import User, UserRole
from app.schemas.api_response import success_response, APIResponse
from app.schemas.chat_schema import ChatRoomCreate, ChatRoomRead, MessageRead, ChatRoomWithMessages

router = APIRouter(prefix="/chat", tags=["Chat"])


# REST endpoints for chat management
@router.post("/rooms", response_model=APIResponse[ChatRoomRead])
@standardize_response
def create_chat_room(*, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new chat room for the current user"""
    # Check if user already has an active chat room
    existing_room = chat_room_crud.get_user_chat_room(db, user_id=current_user.id)
    if existing_room:
        return success_response(
            data=existing_room,
            message="User already has an active chat room",
            status_code=200
        )
    
    # Create a new chat room
    room_data = ChatRoomCreate(
        user_id=current_user.id,
        name=f"{current_user.username}'s Chat"
    )
    
    # Find and assign the least busy expert
    if current_user.role == UserRole.USER:
        print(f"Finding expert for user {current_user.username} (ID: {current_user.id})")
        expert = chat_room_crud.find_least_busy_expert(db)
        if expert:
            print(f"Assigned expert {expert.username} (ID: {expert.id}) to chat room")
            room_data.expert_id = expert.id
        else:
            print("No expert found to assign to chat room")
    
    # Create the chat room
    chat_room = chat_room_crud.create_chat_room(db, obj_in=room_data)
    
    return success_response(
        data=chat_room,
        message="Chat room created successfully",
        status_code=201
    )


@router.get("/rooms/me", response_model=APIResponse[ChatRoomRead])
@standardize_response
def get_my_chat_room(*, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the current user's active chat room"""
    if current_user.role == UserRole.USER:
        chat_room = chat_room_crud.get_user_chat_room(db, user_id=current_user.id)
    elif current_user.role == UserRole.EXPERT:
        # For experts, return their first assigned chat room (if any)
        expert_rooms = chat_room_crud.get_expert_chat_rooms(db, expert_id=current_user.id)
        chat_room = expert_rooms[0] if expert_rooms else None
    elif current_user.role == UserRole.ADMIN:
        # For admins, return the first active chat room (if any)
        admin_rooms = chat_room_crud.get_all_active_chat_rooms(db)
        chat_room = admin_rooms[0] if admin_rooms else None
    else:
        chat_room = None
    
    if not chat_room:
        return success_response(
            message="No active chat room found",
            status_code=404
        )
    
    return success_response(
        data=chat_room,
        message="Chat room retrieved successfully"
    )


@router.get("/rooms/{room_id}", response_model=APIResponse[ChatRoomWithMessages])
@standardize_response
def get_chat_room(
    *,
    room_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a chat room with its messages"""
    chat_room = chat_room_crud.get_chat_room_with_messages(db, room_id=room_id)
    
    if not chat_room:
        return success_response(
            message="Chat room not found",
            status_code=404
        )
    
    # Check if the user has access to this chat room
    if current_user.role != UserRole.ADMIN and current_user.id != chat_room.user_id and current_user.id != chat_room.expert_id:
        raise HTTPException(status_code=403, detail="You don't have access to this chat room")
    
    # Mark messages as read
    message_crud.mark_messages_as_read(db, chat_room_id=room_id, user_id=current_user.id)
    
    return success_response(
        data=chat_room,
        message="Chat room retrieved successfully"
    )


@router.get("/rooms", response_model=APIResponse[List[ChatRoomRead]])
@standardize_response
def get_chat_rooms(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin, UserRole.expert))
):
    """Get all chat rooms (admin) or assigned chat rooms (expert)"""
    if current_user.role == UserRole.admin:
        chat_rooms = chat_room_crud.get_all_active_chat_rooms(db)
    else:  # Expert
        chat_rooms = chat_room_crud.get_expert_chat_rooms(db, expert_id=current_user.id)
    
    return success_response(
        data=chat_rooms,
        message="Chat rooms retrieved successfully"
    )


# WebSocket endpoint for real-time chat
@router.websocket("/ws/{room_id}/{user_id}")
async def chat_endpoint(websocket: WebSocket, room_id: int, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    # Get user and validate
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Get chat room and validate access
    chat_room = chat_room_crud.get_chat_room(db, room_id=room_id)
    if not chat_room:
        await websocket.close(code=1008, reason="Chat room not found")
        return
    
    # Validate user access to the chat room
    if user.role != UserRole.ADMIN and user.id != chat_room.user_id and user.id != chat_room.expert_id:
        await websocket.close(code=1008, reason="Access denied to this chat room")
        return
    
    # Connect to the room
    await manager.connect(websocket, room_id, user.id, user.role)
    
    try:
        # Process messages
        while True:
            data = await websocket.receive_text()
            await manager.process_message(websocket, data, db)
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        manager.disconnect(websocket)
