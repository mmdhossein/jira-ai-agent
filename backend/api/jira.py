# backend/app/api/jira_proxy.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.jira_client import JiraClient
from typing import Optional, List
import os

router = APIRouter(prefix="/jira", tags=["jira"])

def get_jira_client():
    """Dependency to get Jira client instance."""
    return JiraClient(

    )

        # base_url=os.getenv("JIRA_BASE_URL"),
        # email=os.getenv("JIRA_EMAIL"),
        # api_token=os.getenv("JIRA_API_TOKEN")


# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@router.get("/projects")
async def get_projects(jira: JiraClient = Depends(get_jira_client)):
    """
    Get all accessible Jira projects.
    
    Returns:
        List of projects with key, name, and metadata
    """
    try:
        projects = await jira.get_projects()
        return {
            "status": "success",
            "data": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@router.get("/projects/{project_key}")
async def get_project_details(
    project_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get detailed information about a specific project.
    
    Args:
        project_key: Project key (e.g., 'PROJ')
        
    Returns:
        Project details including components, versions, issue types
    """
    try:
        project = await jira.get_project_by_key(project_key)
        return {
            "status": "success",
            "data": project
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Project not found: {str(e)}")


# ============================================================================
# ISSUE ENDPOINTS
# ============================================================================

@router.get("/issues/{issue_key}")
async def get_issue(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get detailed information about a specific issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        
    Returns:
        Complete issue details including fields, comments, attachments
    """
    try:
        issue = await jira.get_issue(issue_key)
        return {
            "status": "success",
            "data": issue
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Issue not found: {str(e)}")


@router.post("/issues")
async def create_issue(
    issue_data: dict,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Create a new Jira issue.
    
    Args:
        issue_data: Issue creation payload (project, summary, description, etc.)
        
    Returns:
        Created issue details
    """
    try:
        issue = await jira.create_issue(issue_data)
        return {
            "status": "success",
            "data": issue,
            "message": "Issue created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create issue: {str(e)}")


@router.put("/issues/{issue_key}")
async def update_issue(
    issue_key: str,
    update_data: dict,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Update an existing Jira issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        update_data: Fields to update
        
    Returns:
        Success message
    """
    try:
        await jira.update_issue(issue_key, update_data)
        return {
            "status": "success",
            "message": f"Issue {issue_key} updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update issue: {str(e)}")


@router.delete("/issues/{issue_key}")
async def delete_issue(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Delete a Jira issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        
    Returns:
        Success message
    """
    try:
        await jira.delete_issue(issue_key)
        return {
            "status": "success",
            "message": f"Issue {issue_key} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete issue: {str(e)}")


@router.post("/issues/{issue_key}/transitions")
async def transition_issue(
    issue_key: str,
    transition_data: dict,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Transition an issue to a different status.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        transition_data: Transition ID and optional fields
        
    Returns:
        Success message
    """
    try:
        await jira.transition_issue(issue_key, transition_data)
        return {
            "status": "success",
            "message": f"Issue {issue_key} transitioned successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to transition issue: {str(e)}")


@router.get("/issues/{issue_key}/transitions")
async def get_transitions(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get available transitions for an issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        
    Returns:
        List of available transitions
    """
    try:
        transitions = await jira.get_transitions(issue_key)
        return {
            "status": "success",
            "data": transitions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get transitions: {str(e)}")


# ============================================================================
# SEARCH & FILTER ENDPOINTS
# ============================================================================

@router.get("/search")
async def search_issues(
    jql: str = Query(..., description="JQL query string"),
    start_at: int = Query(0, description="Starting index"),
    max_results: int = Query(50, description="Maximum results to return"),
    fields: Optional[str] = Query(None, description="Comma-separated field names"),
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Search for issues using JQL (Jira Query Language).
    
    Args:
        jql: JQL query string
        start_at: Pagination start index
        max_results: Maximum number of results
        fields: Specific fields to return
        
    Returns:
        Search results with issues and metadata
    """
    print(f"DEBUG: Calling search_issues with: {jql=}, {start_at=}, {max_results=}, {fields=}")

    try:
        if fields is not None:
            fields = fields.split(",") if isinstance(fields, str) else fields
        results = await jira.search_issues(jql, max_results=max_results, fields=fields)
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")


@router.get("/filters/{filter_id}")
async def get_filter(
    filter_id: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get a saved Jira filter.
    
    Args:
        filter_id: Filter ID
        
    Returns:
        Filter details including JQL
    """
    try:
        filter_data = await jira.get_filter(filter_id)
        return {
            "status": "success",
            "data": filter_data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Filter not found: {str(e)}")


# ============================================================================
# COMMENT ENDPOINTS
# ============================================================================

@router.get("/issues/{issue_key}/comments")
async def get_comments(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get all comments for an issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        
    Returns:
        List of comments
    """
    try:
        comments = await jira.get_comments(issue_key)
        return {
            "status": "success",
            "data": comments
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get comments: {str(e)}")


@router.post("/issues/{issue_key}/comments")
async def add_comment(
    issue_key: str,
    comment_data: dict,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Add a comment to an issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        comment_data: Comment body and metadata
        
    Returns:
        Created comment details
    """
    try:
        comment = await jira.add_comment(issue_key, comment_data)
        return {
            "status": "success",
            "data": comment,
            "message": "Comment added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add comment: {str(e)}")


# ============================================================================
# SPRINT ENDPOINTS (for Scrum projects)
# ============================================================================

@router.get("/boards/{board_id}/sprints")
async def get_sprints(
    board_id: str,
    state: Optional[str] = Query(None, description="Sprint state: active, future, closed"),
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get sprints for a board.
    
    Args:
        board_id: Board ID
        state: Filter by sprint state (active, future, closed)
        
    Returns:
        List of sprints
    """
    try:
        sprints = await jira.get_sprints(board_id, state)
        return {
            "status": "success",
            "data": sprints
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sprints: {str(e)}")


@router.get("/sprints/{sprint_id}/issues")
async def get_sprint_issues(
    sprint_id: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get all issues in a sprint.
    
    Args:
        sprint_id: Sprint ID
        
    Returns:
        List of issues in the sprint
    """
    try:
        issues = await jira.get_sprint_issues(sprint_id)
        return {
            "status": "success",
            "data": issues
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sprint issues: {str(e)}")


# ============================================================================
# BOARD ENDPOINTS
# ============================================================================

@router.get("/boards")
async def get_boards(
    project_key: Optional[str] = Query(None, description="Filter by project key"),
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get all boards, optionally filtered by project.
    
    Args:
        project_key: Optional project key filter
        
    Returns:
        List of boards
    """
    try:
        boards = await jira.get_boards(project_key)
        return {
            "status": "success",
            "data": boards
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get boards: {str(e)}")


# ============================================================================
# USER & ASSIGNMENT ENDPOINTS
# ============================================================================

@router.get("/users/assignable")
async def get_assignable_users(
    project: Optional[str] = Query(None, description="Project key"),
    issue_key: Optional[str] = Query(None, description="Issue key"),
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get users that can be assigned to issues.
    
    Args:
        project: Project key to filter assignable users
        issue_key: Issue key to filter assignable users
        
    Returns:
        List of assignable users
    """
    try:
        users = await jira.get_assignable_users(project, issue_key)
        return {
            "status": "success",
            "data": users
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get users: {str(e)}")


@router.get("/users/search")
async def search_users(
    query: str = Query(..., description="Search query"),
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Search for users.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching users
    """
    try:
        users = await jira.search_users(query)
        return {
            "status": "success",
            "data": users
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search users: {str(e)}")


# ============================================================================
# WORKLOG ENDPOINTS
# ============================================================================

@router.get("/issues/{issue_key}/worklogs")
async def get_worklogs(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get worklogs for an issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        
    Returns:
        List of worklogs
    """
    try:
        worklogs = await jira.get_worklogs(issue_key)
        return {
            "status": "success",
            "data": worklogs
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get worklogs: {str(e)}")


@router.post("/issues/{issue_key}/worklogs")
async def add_worklog(
    issue_key: str,
    worklog_data: dict,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Add a worklog entry to an issue.
    
    Args:
        issue_key: Issue key (e.g., 'PROJ-123')
        worklog_data: Worklog details (timeSpent, comment, started)
        
    Returns:
        Created worklog details
    """
    try:
        worklog = await jira.add_worklog(issue_key, worklog_data)
        return {
            "status": "success",
            "data": worklog,
            "message": "Worklog added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add worklog: {str(e)}")


# ============================================================================
# METADATA ENDPOINTS
# ============================================================================

@router.get("/priorities")
async def get_priorities(jira: JiraClient = Depends(get_jira_client)):
    """Get all issue priorities."""
    try:
        priorities = await jira.get_priorities()
        return {"status": "success", "data": priorities}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get priorities: {str(e)}")


@router.get("/statuses")
async def get_statuses(jira: JiraClient = Depends(get_jira_client)):
    """Get all issue statuses."""
    try:
        statuses = await jira.get_statuses()
        return {"status": "success", "data": statuses}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get statuses: {str(e)}")


@router.get("/issue-types")
async def get_issue_types(
    project_key: Optional[str] = Query(None, description="Filter by project"),
    jira: JiraClient = Depends(get_jira_client)
):
    """Get all issue types, optionally filtered by project."""
    try:
        issue_types = await jira.get_issue_types(project_key)
        return {"status": "success", "data": issue_types}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get issue types: {str(e)}")


# ============================================================================
# ATTACHMENT ENDPOINTS
# ============================================================================

@router.get("/issues/{issue_key}/attachments")
async def get_attachments(
    issue_key: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """Get all attachments for an issue."""
    try:
        attachments = await jira.get_attachments(issue_key)
        return {"status": "success", "data": attachments}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get attachments: {str(e)}")


# ============================================================================
# ANALYTICS ENDPOINTS (for reporting)
# ============================================================================

@router.get("/analytics/velocity")
async def get_velocity(
    board_id: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get velocity data for a board.
    
    Args:
        board_id: Board ID
        
    Returns:
        Velocity metrics
    """
    try:
        velocity = await jira.get_velocity(board_id)
        return {"status": "success", "data": velocity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get velocity: {str(e)}")


@router.get("/analytics/burndown")
async def get_burndown(
    sprint_id: str,
    jira: JiraClient = Depends(get_jira_client)
):
    """
    Get burndown chart data for a sprint.
    
    Args:
        sprint_id: Sprint ID
        
    Returns:
        Burndown data
    """
    try:
        burndown = await jira.get_burndown(sprint_id)
        return {"status": "success", "data": burndown}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get burndown: {str(e)}")
