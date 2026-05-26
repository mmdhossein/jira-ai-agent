# backend/app/schemas/report.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReportResponse(BaseModel):
    id: int
    command_id: int
    project_name: Optional[str]
    report_type: str
    chart_data: Optional[Dict[str, Any]]
    summary: Optional[str]
    language: str
    created_at: datetime
    images: Optional[List[int]] = None  # List of image IDs


class ImageResponse(BaseModel):
    id: int
    report_id: int
    image_type: str
    mime_type: str
    title: Optional[str]
    description: Optional[str]
    created_at: datetime


class PDFGenerateRequest(BaseModel):
    report_id: int
    include_images: bool = True
