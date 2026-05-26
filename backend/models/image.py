# backend/app/models/image.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    
    # Image details
    image_type = Column(String(50), nullable=False)  # bar, pie, line, gantt, etc.
    image_data = Column(LargeBinary, nullable=False)  # PNG/JPEG binary data
    mime_type = Column(String(50), default="image/png")
    
    # Metadata
    title = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="images")
    chat_history = relationship("ChatHistory", back_populates="image")
