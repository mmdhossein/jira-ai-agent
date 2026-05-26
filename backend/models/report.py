# backend/app/models/report.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)  
    command_id = Column(Integer, ForeignKey("commands.id"), nullable=True)
    project_name = Column(String(255), index=True, nullable=False)
    
    # Report content
    report_type = Column(String(100), nullable=False)  # summary, risk, delay, etc.
    chart_data = Column(JSON, nullable=True)  # chart_data for iamge generation
    structured_data = Column(JSON, nullable=True)  # structured_data PDF report 
    
    summary = Column(Text, nullable=True)  # Text summary
    
    # Metadata
    language = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    command = relationship("Command", back_populates="reports")
    images = relationship("Image", back_populates="report", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="report")
