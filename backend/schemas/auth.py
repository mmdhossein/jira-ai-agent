# backend/app/schemas/auth.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class OTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)


class OTPResponse(BaseModel):
    message: str
    mobile: str


class VerifyOTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=4, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    mobile: str
    jira_projects: Optional[List[str]] = None


class TokenData(BaseModel):
    user_id: int
    mobile: str
    jira_session: Optional[Dict[str, Any]] = None
    jira_projects: Optional[List[str]] = None


class UserPreferences(BaseModel):
    email: Optional[str] = None
    language: Optional[str] = "en"
    data_source_config: Optional[Dict[str, Any]] = None


class SendOTPRequest(BaseModel):
    mobile_number: Optional[str] = None


class AuthResponse(BaseModel):
    success: Optional[bool] = None
    token: Optional[str] = None
    user: Optional[dict] = None
    message : Optional[str] = None


