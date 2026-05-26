# Jira AI Agent

An AI-powered Jira assistant with a Chrome extension frontend, Python backend, and n8n automation workflow.

---

## Architecture

Chrome Extension  →  n8n Webhook  →  LLM Pipeline  →  Python Backend (Jira API)

![diagram](img/Jira_AI_Agent_Interface_Dashboard-NotebookLM.html)

**Components:**
- **Chrome Extension** — Chat UI embedded in Jira, sends user messages with page context
- **Python Backend** — REST API wrapping Jira APIs + analytics endpoints
- **n8n Workflow** — Orchestrates intent classification, API planning, data fetching, and response generation

---

## n8n Workflow

The workflow processes chat messages through a multi-stage LLM pipeline:

Webhook → Extract Context → LLM1 Classification → Parse Flags├── [needsProcessing=false] → Simple Response → Return
    └── [needsProcessing=true]
            ├── [ask_help=true]  → LLM4 Help → Return Help
            └── [ask_help=false] → LLM2 API Planning → Prepare API Calls
                                        → Call Jira API → Aggregate Data
                                        → LLM3 Generate → Validate Response → Return Final


### Stages

| Stage | Model | Role |
|---|---|---|
| LLM1 Classification | DeepSeek Chat | Classifies intent flags |
| LLM2 API Planning | GPT-4o | Selects which Jira APIs to call |
| LLM3 Generate | Gemini 2.0 Flash Lite | Generates final response + report |
| LLM4 Help | DeepSeek v4 Flash | Answers Jira how-to questions |

### Intent Flags

| Flag | Meaning |
|---|---|
| `ask_report` | Data analysis, sprints, issues, workloads |
| `ask_recommendation` | Actionable suggestions |
| `ask_prediction` | Forecasts and projections |
| `ask_help` | General Jira questions |
| `ask_chart` | Chart/visualization requested |
| `ask_pdf` | PDF/file export requested |

### Webhook

**POST** `/webhook/chat-intelligence`

```json
{
  "user_id": "string",
  "session_id": "string",
  "message": "string",
  "chat_history": [],
  "current_project": "PROJECT-KEY",
  "page_context": {
    "page_type": "board | backlog | issue | ..."
  }
}
```

**Response**

```json
{
  "success": true,
  "message": "Conversational response",
  "report": {
    "summary": "Executive summary",
    "chart_data": {
      "chart_plan": "bar | line | pie | scatter | histogram | heatmap",
      "title": "Chart Title",
      "labels": ["label1"],
      "values": [42]
    },
    "structured_data": {
      "type": "key_insights",
      "items": [{ "label": "Key Point", "value": "Description" }]
    }
  },
  "flags": {
    "ask_chart": false,
    "ask_pdf": false
  }
}
```

---

## Python Backend

### Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jira/projects` | List all projects |
| GET | `/api/jira/projects/{key}` | Project details |
| GET | `/api/jira/issues/{key}` | Issue details |
| GET | `/api/jira/issues/{key}/changelog` | Issue history |
| GET | `/api/jira/search?jql={query}` | JQL search |
| GET | `/api/jira/sprints` | List sprints |
| GET | `/api/jira/sprints/{id}` | Sprint details |
| GET | `/api/jira/sprints/{id}/issues` | Sprint issues |
| GET | `/api/jira/analytics/velocity?project={key}` | Velocity analytics |
| GET | `/api/jira/analytics/burndown?sprint={id}` | Burndown chart data |
| GET | `/api/jira/users` | List users |
| GET | `/api/jira/users/{id}/workload` | User workload |

### Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

**.env**
```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token
```

---

## 🧩 Chrome Extension

### Setup

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder

### Configuration

Set the n8n webhook URL in the extension settings before use.

---

## 🚀 Getting Started

1. Start the Python backend (`localhost:8000`)
2. Import and activate the n8n workflow
3. Set `baseUrl` in the **Prepare API Calls** node to your backend address
4. Load the Chrome extension
5. Open Jira and start chatting

## Tech Stack

- **Frontend:** Chrome Extension (JS)
- **Orchestration:** n8n
- **Backend:** Python (FastAPI / Flask)
- **LLMs:** GPT-4o, DeepSeek Chat, DeepSeek v4 Flash, Gemini 2.0 Flash Lite
- **Jira:** Atlassian REST API v3