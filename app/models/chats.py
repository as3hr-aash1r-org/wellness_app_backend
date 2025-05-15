# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from app.database.base import Base


# class ChatRoom(Base):
#     __tablename__ = "chat_rooms"

#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     messages = relationship("ChatMessage", back_populates="room", cascade="all, delete")
#     participants = relationship("ChatParticipant", back_populates="room", cascade="all, delete")


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True)
#     room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
#     sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     content = Column(Text, nullable=False)  # audio url, image url
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     room = relationship("ChatRoom", back_populates="messages")
#     sender = relationship("User", back_populates="messages")


# class ChatParticipant(Base):
#     __tablename__ = "chat_participants"

#     id = Column(Integer, primary_key=True)
#     room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

#     room = relationship("ChatRoom", back_populates="participants")
