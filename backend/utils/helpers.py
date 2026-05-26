# backend/app/utils/helpers.py
import uuid
from datetime import datetime
from typing import Optional


def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        UUID string for session identification
    """
    return str(uuid.uuid4())


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string or None
    """
    if dt is None:
        return None
    return dt.strftime(format_str)


def parse_jira_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse Jira datetime string to datetime object.
    
    Args:
        date_str: Jira datetime string
        
    Returns:
        Datetime object or None
    """
    if not date_str:
        return None
    
    try:
        # Jira typically uses ISO 8601 format
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None
