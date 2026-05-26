# backend/app/schemas/jira.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class JiraIssue(BaseModel):
    key: str
    summary: str
    status: str
    assignee: Optional[str]
    priority: Optional[str]
    created: datetime
    updated: datetime
    due_date: Optional[datetime]
    project: str


class JiraProject(BaseModel):
    key: str
    name: str
    description: Optional[str]
    lead: Optional[str]


class JiraQueryRequest(BaseModel):
    jql: str
    fields: Optional[List[str]] = None
    max_results: int = 100


class JiraQueryResponse(BaseModel):
    success: bool
    issues: List[Dict[str, Any]]
    total: int
    error: Optional[str] = None
