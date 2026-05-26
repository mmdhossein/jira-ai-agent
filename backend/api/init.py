# backend/app/api/__init__.py
from fastapi import APIRouter
from app.api import auth, chat, sessions, image, reports, jira

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(sessions.router)
api_router.include_router(image.router)
api_router.include_router(reports.router)
api_router.include_router(jira.router)

__all__ = ["api_router"]
