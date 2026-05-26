```markdown
# 🤖 Jira AI Agent

> An intelligent AI assistant embedded directly in Jira — powered by a multi-LLM pipeline, Python backend, and Chrome extension.

![n8n](https://img.shields.io/badge/n8n-workflow-orange?logo=n8n)
![Python](https://img.shields.io/badge/Python-backend-blue?logo=python)
![Chrome](https://img.shields.io/badge/Chrome-extension-yellow?logo=googlechrome)
![Jira](https://img.shields.io/badge/Jira-integration-0052CC?logo=jira)

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Chrome Extension│────▶│  n8n Webhook     │────▶│  LLM Pipeline       │
│  (Chat UI)      │◀────│  /chat-intel...  │◀────│  Classification     │
└─────────────────┘     └──────────────────┘     │  Planning           │
                                                  │  Generation         │
                                                  └────────┬────────────┘
                                                           │
                                                  ┌────────▼────────────┐
                                                  │  Python Backend     │
                                                  │  Jira REST API      │
                                                  └─────────────────────┘

| Layer | Technology | Role |
|---|---|---|
| 🖥️ Frontend | Chrome Extension | Chat UI embedded in Jira |
| ⚙️ Orchestration | n8n | Multi-LLM pipeline & routing |
| 🐍 Backend | Python (FastAPI) | Jira API wrapper & analytics |
| 🧠 AI | GPT-4o · DeepSeek · Gemini | Classification, planning, generation |

---

## 🔄 n8n Workflow

### Pipeline Overview


📥 Webhook
    └── 🔍 Extract Context
            └── 🧠 LLM1 — Intent Classification (DeepSeek)
                    └── 🚦 Parse Flags
                            │
                            ├── needsProcessing = false
                            │       └── 💬 Simple Response ──────────────────▶ 📤 Return
                            │
                            └── needsProcessing = true
                                    │
                                    ├── ask_help = true
                                    │       └── 🆘 LLM4 Help (DeepSeek) ──────▶ 📤 Return
                                    │
                                    └── ask_help = false
                                            └── 📋 LLM2 API Planning (GPT-4o)
                                                    └── 🔧 Prepare API Calls
                                                            └── 🌐 Call Jira API
                                                                    └── 📊 Aggregate Data
                                                                            └── ✍️ LLM3 Generate (Gemini)
                                                                                    └── ✅ Validate Response
                                                                                            └── 📤 Return Final

### 🧠 LLM Models

| # | Model | Stage | Purpose |
|---|---|---|---|
| 1 | `DeepSeek Chat` | Classification | Detects intent flags from user message |
| 2 | `GPT-4o` | API Planning | Selects which Jira endpoints to call |
| 3 | `Gemini 2.0 Flash Lite` | Generation | Builds final response, charts, summaries |
| 4 | `DeepSeek v4 Flash` | Help | Answers general Jira how-to questions |

### 🚩 Intent Flags

| Flag | Trigger |
|---|---|
| `ask_report` | Sprint data, issue analysis, workload queries |
| `ask_recommendation` | Requests for actionable suggestions |
| `ask_prediction` | Forecasts, projections, estimations |
| `ask_help` | General Jira usage questions |
| `ask_chart` | Visualization or chart requested |
| `ask_pdf` | Export or PDF generation requested |

---

## 🔌 Webhook API

### Request

**`POST`** `/webhook/chat-intelligence`

json
{
  "user_id": "u_123",
  "session_id": "sess_abc",
  "message": "Show me sprint velocity for PROJECT-X",
  "chat_history": [],
  "current_project": "PROJECT-X",
  "page_context": {
    "page_type": "board | backlog | issue | dashboard"
  }
}

### Response

json
{
  "success": true,
  "message": "Here's the velocity trend for PROJECT-X over the last 5 sprints...",
  "report": {
    "summary": "Executive summary of findings",
    "chart_data": {
      "chart_plan": "bar | line | pie | scatter | histogram | heatmap",
      "title": "Sprint Velocity",
      "labels": ["Sprint 1", "Sprint 2", "Sprint 3"],
      "values": [34, 41, 38]
    },
    "structured_data": {
      "type": "key_insights",
      "items": [
        { "label": "Avg Velocity", "value": "37.7 points" }
      ]
    }
  },
  "flags": {
    "ask_chart": true,
    "ask_pdf": false
  }
}

---

## 🐍 Python Backend

### API Endpoints

#### 📁 Projects
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jira/projects` | List all projects |
| `GET` | `/api/jira/projects/{key}` | Project details |

#### 🎫 Issues
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jira/issues/{key}` | Issue details |
| `GET` | `/api/jira/issues/{key}/changelog` | Issue change history |
| `GET` | `/api/jira/search?jql={query}` | JQL search |

#### 🏃 Sprints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jira/sprints` | List sprints |
| `GET` | `/api/jira/sprints/{id}` | Sprint details |
| `GET` | `/api/jira/sprints/{id}/issues` | Issues in sprint |

#### 📊 Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jira/analytics/velocity?project={key}` | Velocity data |
| `GET` | `/api/jira/analytics/burndown?sprint={id}` | Burndown chart data |

#### 👥 Users
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jira/users` | List users |
| `GET` | `/api/jira/users/{id}/workload` | User workload |

### ⚙️ Setup

bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py

**.env**
env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token

> 🔑 Generate your API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

---

## 🧩 Chrome Extension

### Installation

1. Open Chrome and navigate to `chrome://extensions`
2. Toggle **Developer mode** on (top right)
3. Click **Load unpacked**
4. Select the `extension/` folder from this repo

### Configuration

Open the extension settings and set your **n8n webhook URL** before first use.

---

## 🚀 Getting Started


1. 🐍  Start Python backend          →  cd backend && python main.py
2. ⚙️  Import n8n workflow            →  import workflow.json into n8n
3. 🔧  Configure Prepare API Calls   →  set baseUrl to http://localhost:8000
4. 🧩  Load Chrome extension         →  chrome://extensions → Load unpacked
5. 🌐  Open Jira                     →  start chatting with your AI agent

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| 🖥️ Frontend | Chrome Extension (JavaScript) |
| ⚙️ Orchestration | [n8n](https://n8n.io) |
| 🐍 Backend | Python · FastAPI |
| 🤖 LLMs | GPT-4o · DeepSeek Chat · DeepSeek v4 Flash · Gemini 2.0 Flash Lite |
| 📋 Project Management | Atlassian Jira REST API v3 |

---

<p align="center">Built with ❤️ to make Jira actually enjoyable</p>
