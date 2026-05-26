# backend/app/services/n8n_client.py
import httpx
from typing import Dict, Any, Optional
from app.config import get_settings
import json 

settings = get_settings()


class N8NClient:
    """Client for interacting with n8n workflows."""
    
    def __init__(self):
        self.base_url = settings.n8n_webhook_url
        self.dummy_mode = False # settings.dummy_mode
    
    async def process_chat(self, user_id: int, 
                           message: str, session_id: str,
                             current_project:str, chat_history:str) -> Dict[str, Any]:
        """
        Send chat message to n8n for processing.
        
        Args:
            user_id: User ID
            message: User message
            session_id: Session ID
            current_project: Current project name
            chat_history: Chat history
            previous_messages: List of previous messages
            
        Returns:
            Standardized response from n8n
        """
        if self.dummy_mode:
            return self._get_dummy_response(message)
        
        try:
            async with httpx.AsyncClient() as client:
                print("Request: ", json.dumps({
                        "user_id": user_id,
                        "message": message,
                        "session_id": session_id,
                        "current_project": current_project,
                        "chat_history": chat_history,
                    }))
                response = await client.post(
                    f"{self.base_url}",
                    json={
                        "user_id": user_id,
                        "message": message,
                        "session_id": session_id,
                        "current_project": current_project,
                        "chat_history": chat_history,
                    },
                    timeout=180.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "action": None,
                        "data": {},
                        "error": f"n8n returned status {response.status_code}"
                    }
        except Exception as e:
            return {
                "success": False,
                "action": None,
                "data": {},
                "error": str(e)
            }
    
    async def generate_report(self, action: str, jira_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request n8n to generate a report from Jira data.
        
        Args:
            action: Action type (e.g., "bottleneck_analysis")
            jira_data: Structured Jira data
            
        Returns:
            Report data with summary and chart specifications
        """
        if self.dummy_mode:
            return self._get_dummy_report(action)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate-report",
                    json={
                        "action": action,
                        "data": jira_data
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "data": {},
                        "error": f"n8n returned status {response.status_code}"
                    }
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
    
    async def classify_intent(self, message: str) -> Dict[str, Any]:
        """
        Classify user intent using LLM via n8n.
        
        Args:
            message: User message
            
        Returns:
            Classification result with action and parameters
        """
        if self.dummy_mode:
            return {"action": "general_query", "parameters": {}}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/classify-intent",
                    json={"message": message},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"action": "general_query", "parameters": {}}
        except Exception:
            return {"action": "general_query", "parameters": {}}
    
    def _get_dummy_response(self, message: str) -> Dict[str, Any]:
        """
        Generate dummy response for testing without n8n.
        """
        message_lower = message.lower()
        
        if "bottleneck" in message_lower:
            return {
                "success": True,
                "action": "bottleneck_analysis",
                "data": {
                    "message": "I've analyzed the workflow bottlenecks. The 'In Review' stage has the highest concentration of issues.",
                    "report": {
                        "summary": "Bottleneck Analysis:\n- In Review: 15 issues (avg 8 days)\n- In Progress: 12 issues (avg 5 days)\n- To Do: 8 issues",
                        "chart_data": {
                            "bottlenecks": [
                                {"stage": "In Review", "count": 15, "avg_days": 8},
                                {"stage": "In Progress", "count": 12, "avg_days": 5},
                                {"stage": "To Do", "count": 8, "avg_days": 2}
                            ]
                        },
                        "chart_data": {
                            "chart_plan": "bar",
                            "labels": ["In Review", "In Progress", "To Do"],
                            "values": [15, 12, 8]
                        },

                        "structured_data": {   
                            "issue_1": "is bad",
                            "issue_2": "is really bad",
                            "issue_3": "is worse"
                        }
                    }
                },
                "error": None
            }  
        
        elif "overdue" in message_lower:
            return {
                "success": True,
                "action": "overdue_issues",
                "data": {
                    "message": "Found 7 overdue issues across 3 projects.",
                    "report": {
                        "summary": "Overdue Issues:\n- PROJECT-123: Critical bug (5 days overdue)\n- PROJECT-124: Feature request (3 days overdue)\n- PROJECT-125: Documentation (2 days overdue)",
                        "chart_data": {
                            "chart_plan":"",
                            "overdue_issues": [
                                {"key": "PROJECT-123", "summary": "Critical bug", "days_overdue": 5},
                                {"key": "PROJECT-124", "summary": "Feature request", "days_overdue": 3},
                                {"key": "PROJECT-125", "summary": "Documentation", "days_overdue": 2}
                            ]
                        }
                    }
                },
                "error": None
            }
        
        elif "velocity" in message_lower:
            return {
                    "success": True,
                    "action": "velocity_trend",
                    "data": {
                    "message": "Team velocity trend for the last 5 sprints.",
                    "report": {
                        "summary": "Average velocity is stable at 38 points per sprint.",
                        "chart_data": {
                        "chart_plan": "line",
                        "labels": ["S1", "S2", "S3", "S4", "S5"],
                        "values": [35, 40, 38, 42, 39]
                        },
                        "structured_data": {
                        "Sprint 2": "Peak performance due to reduced scope.",
                        "Sprint 4": "Highest velocity, team fully optimized."
                        }
                    }
                    }
                }
        elif "issue distribution" in message_lower:
            return {
                "success": True,
                "action": "issue_distribution",
                "data": {
                "message": "Breakdown of issue types in current project.",
                "report": {
                    "summary": "Focus is currently heavy on new Feature development.",
                    "chart_data": {
                    "chart_plan": "pie",
                    "labels": ["Feature", "Bug", "Task", "Sub-task"],
                    "values": [45, 25, 20, 10]
                    },
                    "structured_data": {
                    "Features": "Primary focus for Q2 release.",
                    "Bugs": "Higher volume due to recent legacy refactor."
                    }
                }
                }
            }
        
        elif "priority vs age" in message_lower:
            return {
            "success": True,
            "action": "priority_vs_age",
            "data": {
            "message": "Scatter analysis of issue age versus priority.",
            "report": {
                "summary": "3 high-priority issues are currently overdue.",
                "chart_data": {
                "chart_plan": "scatter",
                "x": [2, 5, 10, 22, 25, 28, 5, 15],
                "y": [1, 1, 2, 3, 3, 3, 2, 2],
                "sizes": [50, 50, 50, 100, 100, 100, 50, 50]
                },
                "structured_data": {
                "Outliers": "Priority 3 tickets exceeding 20 days.",
                "Resolution": "Immediate action required for aged items."
                }
            }
            }
        }

        elif "workload" in message_lower:
            return  {
            "success": True,
            "action": "workload_heatmap",
            "data": {
            "message": "Workload intensity heatmap by day and hour.",
            "report": {
                "summary": "Peak activity observed mid-week.",
                "chart_data": {
                "chart_plan": "heatmap",
                "matrix": [
                    [1, 5, 2, 0, 1],
                    [2, 8, 4, 1, 2],
                    [3, 10, 6, 2, 1],
                    [1, 6, 3, 1, 0]
                ]
                },
                "structured_data": {
                "Mid-week": "Maximum collaborative capacity reached.",
                "Monday": "Low intensity, primarily planning phase."
                }
            }
            }
        }
                
        else:
            return {
                "success": True,
                "action": "general_query",
                "data": {
                    "message": "I'm here to help with Jira analytics. You can ask about bottlenecks, overdue issues, team performance, and more."
                },
                "error": None
            }
    
    def _get_dummy_report(self, action: str) -> Dict[str, Any]:
        """
        Generate dummy report for testing.
        """
        return {
            "success": True,
            "data": {
                "summary": f"Dummy report for action: {action}",
                "chart_data": {"dummy": True},
                "chart_data": {
                    "type": "bar",
                    "labels": ["A", "B", "C"],
                    "values": [10, 20, 15]
                }
            },
            "error": None
        }
