# backend/app/services/jira_client.py
import httpx
from typing import Optional, List, Dict, Any
from app.config import get_settings
from app.schemas.jira import JiraIssue, JiraProject
import json

settings = get_settings()


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self):
        self.base_url = settings.jira_base_url
        self.username = settings.jira_username
        self.password = settings.jira_password
        self.auth = (self.username, self.password)
        self.Cookie = settings.Cookie
    
    async def test_connection(self) -> bool:
        """  
        Test Jira connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                print("CHECK JIRA CREDENTIALS: ",)
                response = await client.get(
                    f"{self.base_url}/rest/api/2/myself",
                    auth=self.auth,
                    timeout=10.0
                )   
                print("CHECK JIRA CREDENTIALS DONE",)

                return response.status_code == 200
        except Exception as e:
            print("ERROR ON JIRA CONNECTION", e)
            return False
    from typing import Optional

    async def get_project_by_key(self, project_key: str) -> Optional[JiraProject]:
        """
        Get a single Jira project by its key.

        Args:
            project_key: The key of the Jira project (e.g. "TEST", "PROJ").

        Returns:
            JiraProject object if found, otherwise None.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/2/project/{project_key}",
                    auth=self.auth,
                    timeout=10.0
                )

                if response.status_code == 200:
                    p = response.json()
                    return JiraProject(
                        key=p.get("key"),
                        name=p.get("name"),
                        description=p.get("description"),
                        lead=p.get("lead", {}).get("displayName") if p.get("lead") else None
                    )

                # 404 -> project not found
                if response.status_code == 404:
                    return None

                # other errors -> also return None (or raise if you prefer)
                return None

        except Exception:
            # log the exception in real code
            return None

    async def get_projects(self) -> List[JiraProject]:
        """
        Get all accessible Jira projects.
        
        Returns:
            List of JiraProject objects
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/2/project",
                    auth=self.auth,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    projects_data = response.json()
                    return [
                        JiraProject(
                            key=p.get("key"),
                            name=p.get("name"),
                            description=p.get("description"),
                            lead=p.get("lead", {}).get("displayName") if p.get("lead") else None
                        )
                        for p in projects_data
                    ]
                return []
        except Exception:
            return []
    
    async def search_issues(self, jql: str, fields: Optional[List[str]] = None, max_results: int = 100) -> Dict[str, Any]:
        """
        Search Jira issues using JQL.
        
        Args:
            jql: JQL query string
            fields: List of fields to return
            max_results: Maximum number of results
            
        Returns:
            Dictionary with issues and metadata
        """
        try:
            if fields is None:
                fields = ["summary", "status", "assignee", "priority", "created", "updated", "duedate", "project"]
                                    #"fields": fields if isinstance(fields, list) else ["*all"],
                        #"maxResults": max_results

            payload =  json.dumps({"jql": jql})  
            print("REQUEST TO SEND: ", payload)     
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/2/search",
                    auth=self.auth,
                    json={"jql": jql},
                    timeout=300.0
                )  
                   
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "issues": data.get("issues", []),
                        "total": data.get("total", 0),
                        "error": None
                    }
                else:
                    print("EROR from Jira: ", {json.dumps(response.json(), indent=2)})
                    return {
                        "success": False,
                        "issues": [],
                        "total": 0,
                        "error": f"Jira API error: status:{response.status_code}- reason: {json.dumps(response.json(), indent=2)}"
                    }
        except Exception as e:
            return {
                "success": False,
                "issues": [],
                "total": 0,
                "error": str(e)
            }
    
    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific Jira issue by key.
        
        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")
            
        Returns:
            Issue data dictionary or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/2/issue/{issue_key}",
                    auth=self.auth,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
    
    async def get_project_issues(self, project_key: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Get all issues for a specific project.
        
        Args:
            project_key: Jira project key
            max_results: Maximum number of results
            
        Returns:
            Dictionary with issues and metadata
        """
        jql = f"project = {project_key} ORDER BY created DESC"
        return await self.search_issues(jql, max_results=max_results)
    
    async def get_user_assigned_issues(self, username: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Get issues assigned to a specific user.
        
        Args:
            username: Jira username
            max_results: Maximum number of results
            
        Returns:
            Dictionary with issues and metadata
        """
        jql = f"assignee = {username} AND resolution = Unresolved ORDER BY priority DESC"
        return await self.search_issues(jql, max_results=max_results)
    
    async def get_overdue_issues(self, project_key: Optional[str] = None, max_results: int = 100) -> Dict[str, Any]:
        """
        Get overdue issues.
        
        Args:
            project_key: Optional project key to filter by
            max_results: Maximum number of results
            
        Returns:
            Dictionary with issues and metadata
        """
        jql = "duedate < now() AND resolution = Unresolved"
        if project_key:
            jql = f"project = {project_key} AND {jql}"
        jql += " ORDER BY duedate ASC"
        
        return await self.search_issues(jql, max_results=max_results)
    
    async def get_issues_by_status(self, status: str, project_key: Optional[str] = None, max_results: int = 100) -> Dict[str, Any]:
        """
        Get issues by status.
        
        Args:
            status: Issue status (e.g., "In Progress", "Done")
            project_key: Optional project key to filter by
            max_results: Maximum number of results
            
        Returns:
            Dictionary with issues and metadata
        """
        jql = f"status = '{status}'"
        if project_key:
            jql = f"project = {project_key} AND {jql}"
        jql += " ORDER BY updated DESC"
        
        return await self.search_issues(jql, max_results=max_results)
    
    async def create_issue(self, project_key: str, summary: str, issue_type: str = "Task", 
                          description: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Create a new Jira issue.
        
        Args:
            project_key: Jira project key
            summary: Issue summary
            issue_type: Issue type (Task, Bug, Story, etc.)
            description: Issue description
            **kwargs: Additional fields (priority, assignee, etc.)
            
        Returns:
            Created issue data or None
        """
        try:
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "issuetype": {"name": issue_type}
                }
            }
            
            if description:
                payload["fields"]["description"] = description
            
            # Add additional fields
            payload["fields"].update(kwargs)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/2/issue",
                    auth=self.auth,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    return response.json()
                return None
        except Exception:
            return None
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """
        Update a Jira issue.
        
        Args:
            issue_key: Jira issue key
            fields: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"fields": fields}
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/rest/api/2/issue/{issue_key}",
                    auth=self.auth,
                    json=payload,
                    timeout=10.0
                )
                
                return response.status_code == 204
        except Exception:
            return False
    
    async def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to a Jira issue.
        
        Args:
            issue_key: Jira issue key
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"body": comment}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/2/issue/{issue_key}/comment",
                    auth=self.auth,
                    json=payload,
                    timeout=10.0
                )
                
                return response.status_code == 201
        except Exception:
            return False
    
    async def get_issue_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available transitions for an issue.
        
        Args:
            issue_key: Jira issue key
            
        Returns:
            List of available transitions
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions",
                    auth=self.auth,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("transitions", [])
                return []
        except Exception:
            return []
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """
        Transition an issue to a new status.
        
        Args:
            issue_key: Jira issue key
            transition_id: Transition ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"transition": {"id": transition_id}}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions",
                    auth=self.auth,
                    json=payload,
                    timeout=10.0
                )
                
                return response.status_code == 204
        except Exception:
            return False
        
    async def delete_issue(self, issue_key: str) -> bool:
        """
        Delete a Jira issue by its key or ID.

        Args:
            issue_key: Issue key or ID (e.g. "TEST-123").

        Returns:
            True if the issue was deleted successfully, False otherwise.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    auth=self.auth,
                    timeout=10.0,
                )

            # Jira returns 204 No Content on successful delete
            if response.status_code == 204:
                return True

            # Common cases: 401/403 (no permission), 404 (not found)
            # You may want to log response.text here for debugging
            return False

        except Exception:
            # log the exception in real code
            return False
    
    async def get_transitions(self, issue_key: str) -> List[Dict[str, str]]:
        """
        Get all available transitions for a given Jira issue.

        Args:
            issue_key: Key or ID of the Jira issue (e.g. "PROJ-123").

        Returns:
            List of transitions, each as { "id": str, "name": str }.
            Returns an empty list if none or on error.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    timeout=10.0
                )

            if response.status_code == 200:
                data = response.json()
                transitions = data.get("transitions", [])
                return [
                    {
                        "id": t.get("id"),
                        "name": t.get("name")
                    }
                    for t in transitions
                ]

            # e.g. 404 (issue not found), 403 (no permission)
            return []

        except Exception:
            # In production code, you’d log the error
            return []
    async def get_filter(self, filter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Jira saved filter by its ID.

        Args:
            filter_id: The ID of the filter (numeric string).

        Returns:
            A dict representing the filter (id, name, jql, description, owner, etc.)
            or None if not found or error.
        """
        url = f"{self.base_url}/rest/api/2/filter/{filter_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    timeout=10.0
                )

            if response.status_code == 200:
                return response.json()

            # 404 = filter not found, or user has no permission
            return None

        except Exception:
            return None    
        
    async def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a Jira issue.

        Args:
            issue_key: Issue key or ID (e.g. "PROJ-123").

        Returns:
            List of comment objects (each includes id, body, author, created, etc.)
            Returns an empty list on error.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    timeout=10.0
                )

            if response.status_code == 200:
                data = response.json()
                return data.get("comments", [])

            return []  # e.g. 404 (issue not found), 403 (no permission)

        except Exception:
            return []
    async def get_boards(self, project_key: str):
        url = f"{self.base_url}/rest/agile/1.0/board?projectKeyOrId={project_key}"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("values", [])
            return []
        except Exception:
            return []
    
    async def get_sprints(self, board_id: int, state: str = None):
        params = {}
        if state:
            params["state"] = state  # "active", "closed", "future"

        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, params=params, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("values", [])
            return []
        except Exception:
            return []
        
    async def get_sprint_issues(self, sprint_id: int):
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("issues", [])
            return []
        except Exception:
            return []
        
    async def get_assignable_users(self, project: str, issue_key: str = None):
        params = {"project": project}
        if issue_key:
            params["issueKey"] = issue_key

        url = f"{self.base_url}/rest/api/2/user/assignable/search"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, params=params, timeout=10.0)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []
    async def search_users(self, query: str):
        url = f"{self.base_url}/rest/api/2/user/search"
        params = {"query": query}

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, params=params, timeout=10.0)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []
        
    async def get_worklogs(self, issue_key: str):
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/worklog"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("worklogs", [])
            return []
        except Exception:
            return []
    
    async def add_worklog(self, issue_key: str, worklog_data: dict):
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/worklog"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    url, json=worklog_data, auth=self.auth, timeout=10.0
                )
            return res.status_code in (200, 201)
        except Exception:
            return False
  
    async def get_statuses(self):
        url = f"{self.base_url}/rest/api/2/status"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []


    async def get_issue_types(self, project_key: str):
        url = f"{self.base_url}/rest/api/2/issue/createmeta?projectKeys={project_key}&expand=projects.issuetypes"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)

            if res.status_code == 200:
                projects = res.json().get("projects", [])
                if projects:
                    return projects[0].get("issuetypes", [])
            return []
        except Exception:
            return []
        
    async def get_attachments(self, issue_key: str):
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)

            if res.status_code == 200:
                fields = res.json().get("fields", {})
                return fields.get("attachment", [])
            return []
        except Exception:
            return []
    async def get_velocity(self, board_id: int):
        url = f"{self.base_url}/rest/greenhopper/1.0/rapid/charts/velocity?rapidViewId={board_id}"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None
        
    async def get_burndown(self, sprint_id: int):
        url = f"{self.base_url}/rest/greenhopper/1.0/rapid/charts/sprintreport? sprintId={sprint_id}"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, auth=self.auth, timeout=10.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None
