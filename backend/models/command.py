# backend/app/models/command.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Command(Base):
    __tablename__ = "commands"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), index=True, nullable=False)
    
    # Command details
    query = Column(Text, nullable=False)  # Original user query
    action = Column(String(100), nullable=True)  # Classified action
    sub_action = Column(String(100), nullable=True)  # Sub-action
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="commands")
    reports = relationship("Report", back_populates="command", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="command")
