# backend/app/models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message details
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Optional links to other entities
    command_id = Column(Integer, ForeignKey("commands.id"), nullable=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    command = relationship("Command", back_populates="chat_history")
    report = relationship("Report", back_populates="chat_history")
    image = relationship("Image", back_populates="chat_history")
