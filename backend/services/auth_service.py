# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import TokenData
from app.config import get_settings
from datetime import datetime
from typing import Optional

settings = get_settings()


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def verify_otp( mobile: str, otp: str) -> bool:
        """
        Verify OTP code (hardcoded for now).
        
        Args:
            mobile: User's mobile number
            otp: OTP code to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """

        return {"success": otp == settings.otp_code}
    
    @staticmethod
    def get_or_create_user(db: Session, mobile: str) -> User:
        """
        Get existing user or create new one.
        
        Args:
            db: Database session
            mobile: User's mobile number
            
        Returns:
            User object
        """
        user = db.query(User).filter(User.mobile == mobile).first()
        
        if not user:
            user = User(
                mobile=mobile,
                language="en",
                preferences={}
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def update_user_jira_session(db: Session, user_id: int, jira_session: dict, jira_projects: list):
        """
        Update user's Jira session data.
        
        Args:
            db: Database session
            user_id: User ID
            jira_session: Jira session data
            jira_projects: List of accessible Jira projects
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.jira_session = jira_session
            user.jira_projects = jira_projects
            db.commit()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user_preferences(db: Session, user_id: int, preferences: dict):
        """
        Update user preferences.
        
        Args:
            db: Database session
            user_id: User ID
            preferences: Dictionary of preferences to update
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Merge with existing preferences
            current_prefs = user.preferences or {}
            current_prefs.update(preferences)
            user.preferences = current_prefs
            
            # Update specific fields if provided
            if "email" in preferences:
                user.email = preferences["email"]
            if "language" in preferences:
                user.language = preferences["language"]
            
            db.commit()
    @staticmethod
    def send_otp(mobile: str, otp: str) -> bool:
        """
        Send OTP code (hardcoded for now).
        
        Args:
            mobile: User's mobile number
            otp: OTP code to verify
            
        Returns:
            {"success":True}
        """
        return {"success":True}