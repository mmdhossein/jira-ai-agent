# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    language = Column(String(10), default="en")  # en or fa
    
    # Jira session data (stored as JSON)
    jira_session = Column(JSON, nullable=True)
    jira_projects = Column(JSON, nullable=True)  # List of accessible projects
    
    # Preferences
    preferences = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    commands = relationship("Command", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
