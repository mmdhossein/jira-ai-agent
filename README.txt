Here's the revised README:

---

# 🤖 Jira AI Agent

![n8n](https://img.shields.io/badge/n8n-workflow-orange?logo=n8n) ![Python](https://img.shields.io/badge/Python-FastAPI-blue?logo=python) ![Chrome](https://img.shields.io/badge/Chrome-Extension-yellow?logo=googlechrome) ![Jira](https://img.shields.io/badge/Jira-Integration-0052CC?logo=jira)

An intelligent Jira assistant powered by multi-model AI. Ask questions, get reports, request predictions, and generate charts — all from a Chrome extension sidebar.

---

## 🏗 Architecture

The system has four layers working together:

| Layer | Technology |
|---|---|
| Frontend | Chrome Extension |
| Orchestration | n8n |
| Backend | Python (FastAPI) |
| AI Models | GPT-4o · DeepSeek · Gemini 2.0 |

The Chrome extension captures your message and Jira context, sends it to an n8n webhook, which classifies intent, fetches data from the Python backend, and returns a structured AI-generated response.

---

## ⚙️ n8n Workflow

The workflow is a sequential pipeline triggered by a webhook. Here's what each stage does:

**1. Webhook & Context Extraction**
Receives the user message along with session info, current Jira project, page context, and recent chat history.

**2. Intent Classification (DeepSeek Chat)**
An LLM classifies the message into one or more intent flags: report request, recommendation, prediction, PDF export, chart generation, or general help. It also detects the language (English or Persian).

**3. Parse & Route**
Flags are parsed and the workflow branches:
- Simple messages (greetings, thanks) → a warm short reply
- Help/how-to questions → a Jira knowledge assistant
- Data requests → the full API pipeline

**4. API Planning (GPT-4o)**
For data requests, GPT-4o decides which backend endpoints to call based on the user's intent and current project context.

**5. Jira Data Fetching**
The planned API calls are executed against the Python backend, which proxies to your Jira instance.

**6. Response Generation (Gemini 2.0 Flash Lite)**
The aggregated Jira data is passed to Gemini, which produces a conversational message plus a structured report with summary, chart data, and key insights.

**7. Validation & Return**
The response is validated (chart type and data shape are checked), then returned to the extension.

---

## 🐍 Python Backend

Proxies requests to Jira and exposes these endpoints:

**Projects**
- `GET /api/jira/projects` — list all projects
- `GET /api/jira/projects/{key}` — project details

**Issues**
- `GET /api/jira/issues/{key}` — issue details
- `GET /api/jira/issues/{key}/changelog` — issue history
- `GET /api/jira/search?jql={query}` — JQL search

**Sprints**
- `GET /api/jira/sprints` — all sprints
- `GET /api/jira/sprints/{id}` — sprint details
- `GET /api/jira/sprints/{id}/issues` — sprint issues

**Analytics**
- `GET /api/jira/analytics/velocity?project={key}`
- `GET /api/jira/analytics/burndown?sprint={id}`

**Users**
- `GET /api/jira/users`
- `GET /api/jira/users/{id}/workload`

### Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

**.env**
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token


Get your API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

---

## 🧩 Chrome Extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` folder
4. Open any Jira page and click the extension icon
5. Configure the webhook URL in extension settings

---

## 🚀 Getting Started

1. Start the Python backend
2. Import the n8n workflow JSON and activate it
3. Update the base URL in the **Prepare API Calls** node to match your backend
4. Load the Chrome extension
5. Open Jira and start chatting

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| n8n | Workflow orchestration |
| FastAPI | Jira proxy backend |
| DeepSeek Chat | Intent classification |
| GPT-4o | API planning |
| Gemini 2.0 Flash Lite | Response generation |
| Chrome Extension | User interface |

---

<div align="center">Built with ❤️ to make Jira actually enjoyable</div>
