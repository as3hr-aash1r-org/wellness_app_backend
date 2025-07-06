from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, desc, and_
from sqlalchemy.orm import Session, joinedload

from app.models.chat import ChatRoom, Message
from app.models.user import User, UserRole
from app.schemas.chat_schema import ChatRoomCreate, MessageCreate


class CRUDChatRoom:
    def create_chat_room(self, db: Session, *, obj_in: ChatRoomCreate) -> ChatRoom:
        """Create a new chat room"""
        db_obj = ChatRoom(
            name=obj_in.name,
            user_id=obj_in.user_id,
            expert_id=obj_in.expert_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_chat_room(self, db: Session, *, room_id: int) -> Optional[ChatRoom]:
        """Get a chat room by ID"""
        query = select(ChatRoom).where(ChatRoom.id == room_id)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_chat_room_with_messages(self, db: Session, *, room_id: int) -> Optional[ChatRoom]:
        """Get a chat room with its messages"""
        # First get the chat room
        query = select(ChatRoom).where(ChatRoom.id == room_id)
        result = db.execute(query)
        chat_room = result.scalar_one_or_none()
        
        if not chat_room:
            return None
            
        # Then get the messages separately with proper ordering
        messages_query = select(Message).where(Message.room_id == room_id).order_by(
            desc(Message.created_at)
        ).options(
            joinedload(Message.sender)
        )
        messages_result = db.execute(messages_query)
        chat_room.messages = list(messages_result.scalars().all())
        
        return chat_room
    
    def get_user_chat_room(self, db: Session, *, user_id: int) -> Optional[ChatRoom]:
        """Get a user's chat room"""
        query = select(ChatRoom).where(
            and_(
                ChatRoom.user_id == user_id,
                ChatRoom.is_active == True
            )
        ).options(
            joinedload(ChatRoom.user),
        ).order_by(desc(ChatRoom.updated_at))
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_expert_chat_rooms(self, db: Session, *, expert_id: int) -> List[ChatRoom]:
        """Get all chat rooms assigned to an expert with user relationship loaded"""
        query = select(ChatRoom).where(
            and_(
                ChatRoom.expert_id == expert_id,
                ChatRoom.is_active == True
            )
        ).options(
            joinedload(ChatRoom.user)  # Eager load the user relationship
        ).order_by(desc(ChatRoom.updated_at))
        
        result = db.execute(query).unique()
        return list(result.scalars().all())
    
    def get_all_active_chat_rooms(self, db: Session) -> List[ChatRoom]:
        """Get all active chat rooms (for admin)"""
        query = select(ChatRoom).where(ChatRoom.is_active == True).order_by(desc(ChatRoom.updated_at))
        result = db.execute(query)
        return list(result.scalars().all())
    
    def assign_expert(self, db: Session, *, room_id: int, expert_id: int) -> ChatRoom:
        """Assign an expert to a chat room"""
        chat_room = self.get_chat_room(db, room_id=room_id)
        if chat_room:
            chat_room.expert_id = expert_id
            chat_room.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(chat_room)
        return chat_room
    def get_available_experts(self, db: Session) -> List[User]:
        """Get all available experts"""
        query = select(User).where(User.role == UserRole.expert)
        result = db.execute(query)
        return list(result.scalars().all())
    
    def find_least_busy_expert(self, db: Session) -> Optional[User]:
        """Find the expert with the fewest active chat rooms"""
        experts = self.get_available_experts(db)
        if not experts:
            print("No experts available in the system")
            return None
            
        expert_load = {}
        for expert in experts:
            query = select(ChatRoom).where(
                and_(
                    ChatRoom.expert_id == expert.id,
                    ChatRoom.is_active == True
                )
            )
            result = db.execute(query)
            expert_load[expert.id] = len(list(result.scalars().all()))
            
        if not expert_load:
            # This should not happen, but just in case
            print("Could not calculate expert load")
            return experts[0]  # Return the first expert if we can't calculate load
            
        # Find expert with minimum load
        min_load_expert_id = min(expert_load, key=expert_load.get)
        expert = db.execute(select(User).where(User.id == min_load_expert_id)).scalar_one_or_none()
        
        print(f"Selected expert: {expert.username if expert else 'None'}")
        return expert


class CRUDMessage:
    def create_message(self, db: Session, *, obj_in: MessageCreate) -> Message:
        """Create a new message"""
        db_obj = Message(
            type=obj_in.type,
            room_id=obj_in.room_id,
            sender_id=obj_in.sender_id,
            content=obj_in.content,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update the chat room's updated_at timestamp
        chat_room = db.execute(select(ChatRoom).where(ChatRoom.id == obj_in.room_id)).scalar_one_or_none()
        if chat_room:
            chat_room.updated_at = datetime.utcnow()
            db.commit()
            
        return db_obj
    
    def get_messages(self, db: Session, *, room_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages for a chat room with pagination"""
        query = select(Message).where(Message.room_id == room_id).order_by(
            desc(Message.created_at)
        ).offset(offset).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())
    
    def mark_messages_as_read(self, db: Session, *, room_id: int, user_id: int) -> int:
        """Mark all messages in a chat room as read for a user"""
        # Get all unread messages not sent by the user
        query = select(Message).where(
            and_(
                Message.room_id == room_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        )
        result = db.execute(query)
        messages = list(result.scalars().all())
        
        # Mark messages as read
        count = 0
        for message in messages:
            message.is_read = True
            count += 1
            
        if count > 0:
            db.commit()
            
        return count
    
    def get_chat_room_users(self, db: Session, *, room_id: int) -> List[User]:
        """Get all users in a chat room (user and expert)"""
        chat_room = self.get_chat_room(db, room_id=room_id)
        if not chat_room:
            return []
            
        users = []
        
        # Add the user who created the chat room
        user = user_crud.get_user_by_id(db, user_id=chat_room.user_id)
        if user:
            users.append(user)
            
        # Add the expert if assigned
        if chat_room.expert_id:
            expert = user_crud.get_user_by_id(db, user_id=chat_room.expert_id)
            if expert:
                users.append(expert)
                
        return users
    
    def get_other_chat_room_users(self, db: Session, *, room_id: int, current_user_id: int) -> List[User]:
        """Get all users in a chat room except the current user"""
        all_users = self.get_chat_room_users(db, room_id=room_id)
        return [user for user in all_users if user.id != current_user_id]


chat_room_crud = CRUDChatRoom()
message_crud = CRUDMessage()
