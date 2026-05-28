# 🤖 Multi-Agent A2A System

[![CI Pipeline](https://github.com/Diptanil-x-42/multi-agent-a2a/actions/workflows/ci.yml/badge.svg)](https://github.com/Diptanil-x-42/multi-agent-a2a/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-Agent%20Dev%20Kit-4285F4?logo=google&logoColor=white)
![A2A Protocol](https://img.shields.io/badge/protocol-A2A-blueviolet)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A multi-agent task delegation system powered by **Google ADK** where specialized agents communicate via the **Agent-to-Agent (A2A)** protocol. An orchestrator intelligently routes user requests to the right specialist — no manual wiring required.

---

## ✨ Features

- 🌦️ **Weather Agent** — Real-time weather data for any city worldwide (Open-Meteo API)
- 🐙 **GitHub Insights Agent** — Repository stats, open issues, and project health (GitHub API)
- 🧠 **Orchestrator Agent** — Discovers remote agents and routes requests automatically
- 📡 **A2A Protocol** — Agents expose auto-generated Agent Cards for capability discovery
- ⚡ **Streaming Support** — Custom Agent Cards with `streaming=true` for real-time responses
- 🩺 **Health-Check Endpoint** — Async `/health` endpoint that probes all agents and reports status
- 🔍 **Agent Discovery Tool** — `list_agents` tool fetches live Agent Cards at runtime
- 🔄 **CI/CD** — GitHub Actions pipeline with Ruff linting + Pytest on every push

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER REQUEST                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │    🧠 Orchestrator Agent     │
        │         :8000               │
        │                             │
        │  • Routes to specialists    │
        │  • list_agents tool         │
        │  • Combines multi-agent     │
        │    responses                │
        └──────┬──────────────┬───────┘
               │              │
          A2A  │              │  A2A
               ▼              ▼
  ┌────────────────┐  ┌─────────────────────┐
  │ 🌦️ Weather     │  │ 🐙 GitHub Insights   │
  │ Agent :8001    │  │    Agent :8002       │
  │                │  │                     │
  │ streaming=true │  │ streaming=true      │
  │ Skills:        │  │ Skills:             │
  │ • get_weather  │  │ • get_repo_info     │
  │                │  │ • get_open_issues   │
  └───────┬────────┘  └──────────┬──────────┘
          │                      │
          ▼                      ▼
   ┌──────────────┐     ┌──────────────┐
   │  Open-Meteo  │     │  GitHub API  │
   │     API      │     │              │
   └──────────────┘     └──────────────┘
```

Each agent runs as an independent A2A server with its own **Agent Card** at `/.well-known/agent-card.json`, enabling dynamic capability discovery.

---

## 📁 Project Structure

```
multi-agent-a2a/
├── weather_agent/
│   └── agent.py              # Weather tool + A2A server (port 8001)
├── github_agent/
│   └── agent.py              # GitHub tools + A2A server (port 8002)
├── orchestrator/
│   ├── __init__.py            # Package init
│   ├── agent.py               # Orchestrator with remote agents + list_agents tool
│   └── health.py              # FastAPI health-check endpoint
├── tests/
│   └── test_tools.py          # Unit tests for all tool functions
├── .github/
│   └── workflows/
│       └── ci.yml             # CI pipeline (lint + test)
├── test_connection.py         # Gemini API connectivity check
├── requirements.txt           # Python dependencies
├── ruff.toml                  # Ruff linter configuration
├── pytest.ini                 # Pytest configuration
├── .env.example               # Environment variable template
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A **Google API Key** with access to Gemini models ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/Diptanil-x-42/multi-agent-a2a.git
cd multi-agent-a2a
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:

```
GOOGLE_API_KEY=your-api-key-here
```

### 5. Verify API Connection

```bash
python test_connection.py
```

You should see:
```
API connection successful!
Response: Hello! ...
```

---

## ▶️ Running the Agents

You need **three terminals** — one for each agent. Start them in this order:

### Terminal 1 — Weather Agent (port 8001)

```bash
uvicorn weather_agent.agent:a2a_app --host 0.0.0.0 --port 8001
```

### Terminal 2 — GitHub Insights Agent (port 8002)

```bash
uvicorn github_agent.agent:a2a_app --host 0.0.0.0 --port 8002
```

### Terminal 3 — Orchestrator Agent (port 8000)

```bash
adk web orchestrator
```

This launches the ADK web interface where you can interact with the orchestrator.

---

## 💬 Usage Examples

Once all agents are running, interact with the orchestrator through the ADK web UI:

| Query | Routed To | What You Get |
|-------|-----------|--------------|
| *"What's the weather in Tokyo?"* | Weather Agent | Temperature, wind speed, humidity |
| *"Tell me about the google/adk-python repo"* | GitHub Agent | Stars, forks, language, description |
| *"What are the open issues in google/adk-python?"* | GitHub Agent | Recent open issues with labels and links |
| *"What agents are available?"* | `list_agents` tool | Live list of all discovered agents and their skills |
| *"Weather in London and issues in google/adk-python"* | Both agents | Combined weather + GitHub results |

---

## 🔍 Agent Discovery

Each agent exposes an **Agent Card** at the well-known endpoint:

```bash
# Weather Agent Card
curl http://localhost:8001/.well-known/agent-card.json

# GitHub Insights Agent Card
curl http://localhost:8002/.well-known/agent-card.json
```

The orchestrator also has a `list_agents` tool that dynamically fetches all Agent Cards and returns a structured summary of available agents, their skills, and streaming capabilities.

---

## 🩺 Health Check

The project includes an async health-check endpoint that probes all registered agents:

```bash
uvicorn orchestrator.health:health_app --port 8003
```

Then query it:

```bash
curl http://localhost:8003/health
```

**Example response:**

```json
{
  "overall_status": "healthy",
  "agents": {
    "weather_agent": {
      "status": "healthy",
      "description": "An agent that provides current weather information for any city worldwide.",
      "streaming": true
    },
    "github_agent": {
      "status": "healthy",
      "description": "An agent that provides GitHub repository insights...",
      "streaming": true
    }
  }
}
```

Returns `"degraded"` if any agent is unreachable or unhealthy.

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Lint

```bash
ruff check .
```

### Test Output

```
tests/test_tools.py::test_get_weather_valid_city         PASSED
tests/test_tools.py::test_get_weather_invalid_city        PASSED
tests/test_tools.py::test_get_repo_info_valid             PASSED
tests/test_tools.py::test_get_repo_info_invalid           PASSED
tests/test_tools.py::test_get_open_issues_valid           PASSED
tests/test_tools.py::test_get_open_issues_respects_max    PASSED
```

> **Note:** Tests call live APIs (Open-Meteo, GitHub). They require internet access and may be subject to rate limits.

---

## 🔄 CI/CD

The project includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) that runs on every push and pull request to `main`:

1. **Checkout** code
2. **Set up** Python 3.12
3. **Install** dependencies
4. **Lint** with Ruff
5. **Test** with Pytest

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| [Google ADK](https://github.com/google/adk-python) | Agent Development Kit for building AI agents |
| [A2A Protocol](https://github.com/google/A2A) | Agent-to-Agent communication protocol |
| [Gemini 2.5 Flash](https://ai.google.dev/) | LLM powering all agents |
| [FastAPI](https://fastapi.tiangolo.com/) | Health-check endpoint |
| [Open-Meteo API](https://open-meteo.com/) | Free weather data (no API key required) |
| [GitHub REST API](https://docs.github.com/en/rest) | Repository and issues data |
| [Ruff](https://docs.astral.sh/ruff/) | Python linter |
| [Pytest](https://docs.pytest.org/) | Test framework |
| [GitHub Actions](https://github.com/features/actions) | CI/CD pipeline |

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Google Agent Development Kit (ADK)](https://github.com/google/adk-python) for the agent framework
- [A2A Protocol](https://github.com/google/A2A) for the agent communication standard
- [Open-Meteo](https://open-meteo.com/) for the free weather API
