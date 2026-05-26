# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str = Field(..., min_length=1)
    project_name: Optional[str] = None


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
    command_id: Optional[int] = None
    report_id: Optional[int] = None
    image_id: Optional[int] = None


class ChatResponse(BaseModel):
    success: bool
    action: str  # "chat", "generate_report", "show_chart", "error"
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    command_id: Optional[int] = None
    report_id: Optional[int] = None
    image_ids: Optional[List[int]] = None
    generate_image: Optional[bool]=False
    generate_pdf : Optional[bool]=False
    flags:Optional[Dict[str, Any]] = None


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]
    total_messages: int


class RecentCommandsResponse(BaseModel):
    commands: List[Dict[str, Any]]
    total: int


class SessionResponse(BaseModel):
    """Response model for chat sessions."""
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True  # For SQLAlchemy ORM compatibility


class MessageResponse(BaseModel):
    """Response model for individual messages."""
    id: int
    session_id: int
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionWithMessages(SessionResponse):
    """Session response with all messages included."""
    messages: List[MessageResponse] = []
