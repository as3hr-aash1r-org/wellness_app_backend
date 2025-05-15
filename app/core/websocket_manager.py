import json
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.crud.chat_crud import chat_room_crud, message_crud
from app.crud.user_crud import user_crud
from app.models.user import UserRole
from app.schemas.chat_schema import WSMessage, WSResponse, MessageCreate


class ConnectionManager:
    def __init__(self):
        # Map of room_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Map of WebSocket -> (user_id, room_id)
        self.connection_details: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, user_role: UserRole):
        """Connect a user to a chat room"""
        await websocket.accept()
        
        # Initialize room if it doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            
        # Add the connection to the room
        self.active_connections[room_id].add(websocket)
        
        # Store connection details
        self.connection_details[websocket] = {
            "user_id": user_id,
            "room_id": room_id,
            "role": user_role
        }
        
        print(f"User {user_id} connected to room {room_id} as {user_role}")
        
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from a chat room"""
        # Get connection details before removing
        details = self.connection_details.get(websocket)
        if details:
            room_id = details["room_id"]
            user_id = details["user_id"]
            user_role = details["role"]
            
            # Remove from active connections
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                # Clean up empty rooms
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            # Remove connection details
            del self.connection_details[websocket]
            
            print(f"User {user_id} disconnected from room {room_id}")
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection"""
        await websocket.send_text(message)
        
    async def broadcast(self, message: str, room_id: int, exclude: Optional[WebSocket] = None):
        """Broadcast a message to all connections in a room"""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != exclude:  # Don't send back to sender if excluded
                    await connection.send_text(message)
                    
    async def handle_join(self, message: WSMessage, db: Session):
        """Handle a user joining a chat room"""
        # Get user details
        user = user_crud.get_user_by_id(db, user_id=message.sender_id)
        if not user:
            return None
            
        # Create response
        response = WSResponse(
            type="join",
            room_id=message.room_id,
            sender_id=user.id,
            sender_name=user.username,
            sender_role=user.role,
            content=f"{user.username} has joined the chat",
            timestamp=datetime.utcnow()
        )
        
        return response
        
    async def handle_message(self, message: WSMessage, db: Session):
        """Handle a chat message and save to database"""
        # Get user details
        user = user_crud.get_user_by_id(db, user_id=message.sender_id)
        if not user or not message.content or not message.room_id:
            return None
            
        # Save message to database
        msg_create = MessageCreate(
            chat_room_id=message.room_id,
            sender_id=message.sender_id,
            content=message.content
        )
        db_message = message_crud.create_message(db, obj_in=msg_create)
        
        # Create response
        response = WSResponse(
            type="text",
            room_id=message.room_id,
            sender_id=user.id,
            sender_name=user.username,
            sender_role=user.role,
            content=message.content,
            timestamp=db_message.created_at,
            message_id=db_message.id
        )
        
        return response
        
    async def handle_assign_expert(self, message: WSMessage, db: Session):
        """Handle assigning an expert to a chat room"""
        if not message.room_id or not message.content:  # content contains expert_id
            return None
            
        try:
            expert_id = int(message.content)
            # Update the chat room
            chat_room = chat_room_crud.assign_expert(db, room_id=message.room_id, expert_id=expert_id)
            if not chat_room:
                return None
                
            # Get expert details
            expert = user_crud.get_user_by_id(db, user_id=expert_id)
            if not expert:
                return None
                
            # Create response
            response = WSResponse(
                type="assign_expert",
                room_id=message.room_id,
                sender_id=message.sender_id,
                sender_name="System",
                sender_role=UserRole.ADMIN,
                content=f"{expert.username} has been assigned as your expert",
                timestamp=datetime.utcnow()
            )
            
            return response
        except ValueError:
            return None
            
    async def process_message(self, websocket: WebSocket, data: str, db: Session):
        """Process an incoming WebSocket message"""
        try:
            # Parse the message
            message_data = json.loads(data)
            message = WSMessage(**message_data)
            
            # Get connection details
            details = self.connection_details.get(websocket)
            if not details:
                return
                
            # Handle different message types
            response = None
            if message.type == "text":
                response = await self.handle_message(message, db)
            elif message.type == "join":
                response = await self.handle_join(message, db)
            elif message.type == "assign_expert" and details["role"] == UserRole.ADMIN:
                response = await self.handle_assign_expert(message, db)
                
            # Broadcast the response if available
            if response and message.room_id in self.active_connections:
                response_json = response.model_dump_json()
                await self.broadcast(response_json, message.room_id)
                
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            await websocket.send_text(json.dumps({"error": str(e)}))


# Create a global connection manager instance
manager = ConnectionManager()
