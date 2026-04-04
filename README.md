# Multi-Agent Assistant

A highly capable AI assistant built with Google Agent Development Kit (ADK) and Model Context Protocol (MCP). It is "Cloud Native" and ready for deployment to Google Cloud Run, utilizing Google AlloyDB for robust database storage.

## Features

- **Multi-Agent Orchestration**: Uses a central `Orchestrator` agent to plan and execute tasks.
- **Local & Cloud Database Integration**: Stores and retrieves tasks using SQLite locally, and automatically switches to AlloyDB when deployed to Google Cloud.
- **MCP Tool Integration**: Built-in mock MCP tools for Calendar and Notes management, controlled via environment variables.
- **Multiple Interfaces**: 
  - **ADK Web UI**: Interactive debugging and tracing interface (`adk web`).
  - **CLI Mode**: Interactive terminal chat.
  - **API Mode**: FastAPI backend for integration with other services.
- **Session Management**: Persistent conversation history using ADK's `InMemorySessionService`.

## Project Structure

```text
├── app/
│   ├── agent.py         # Central logic for the Orchestrator Agent and ADK Runner
│   ├── main.py          # FastAPI server implementation
│   ├── cli.py           # Command-line interface
│   └── tools/
│       ├── db_tool.py   # SQLAlchemy-based DB operations (AlloyDB + SQLite fallback)
│       └── mcp_tools.py # MCP service integrations (Calendar, Notes)
├── .adk.yaml            # ADK configuration for agent discovery
├── .env                 # Environment configuration (API keys, DB settings, feature toggles)
├── .gitignore           # Git ignore rules
├── Dockerfile           # Containerization configuration for Google Cloud Run
└── requirements.txt     # Python dependencies
```

## Setup & Local Development

1. **Clone the repository** and navigate to the project directory.
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Create or edit the `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   CALENDAR_ENABLED=true
   NOTES_ENABLED=true
   ```

## Usage Modes

### 1. ADK Web Interface (Recommended for Development)
Run the ADK's built-in web server to interact with the agent and view detailed execution traces. This is the recommended mode for Hackathons as it visually demonstrates the agent's thought process.
```bash
adk web
```
*Access the Dev UI at `http://127.0.0.1:8000`.*

### 2. Command-Line Interface (CLI)
Run the interactive terminal chat:
```bash
python app/cli.py
```

### 3. API Mode (FastAPI)
Start the FastAPI server for programmatic access:
```bash
python app/main.py
```
*The API will be available at `http://localhost:8000/chat`. Swagger docs at `/docs`.*

## Cloud Deployment (Google Cloud Run & AlloyDB)

This project is configured to be seamlessly deployed to Google Cloud. The `db_tool.py` automatically detects when it is running in Cloud Run (via the `K_SERVICE` environment variable) and switches from local SQLite to Google AlloyDB via the AlloyDB Python Connector.

### Prerequisites for Cloud
- A Google Cloud Project with Billing enabled.
- Cloud Run and AlloyDB APIs enabled.
- An AlloyDB Cluster and Instance created.
- The `google-cloud-alloydb-connector` and `pg8000` drivers installed (included in `requirements.txt`).

### Deployment Steps
1. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy multi-agent-assistant \
     --source . \
     --port 8080 \
     --set-env-vars GOOGLE_API_KEY=your_api_key,ALLOYDB_INSTANCE_NAME=your_connection_name,DB_USER=postgres,DB_PASS=your_password,DB_NAME=assistant_db
   ```

## Recent Updates
- **Cloud Native Architecture**: Integrated `google-cloud-alloydb-connector` for seamless Cloud Run deployments.
- **Dockerized**: Added a `Dockerfile` exposing port `8080` for Cloud Run.
- **Refactored Agent Discovery**: Fixed ADK agent discovery issues (`No root_agent found`) by strictly adhering to ADK naming conventions (`root_agent` and `.adk.yaml`).
- **Model Stability**: Set the default model to `gemini-1.5-flash` for optimal streaming compatibility in the ADK Web UI.
- **Clean Workspace**: Removed all unused test scripts, local database files, and redundant ADK folders to ensure a clean codebase for submission.
