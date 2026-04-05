# 🤖 Multi-Agent Assistant Team

A sophisticated, production-grade AI assistant system built with the **Google Agent Development Kit (ADK)** and **Model Context Protocol (MCP)**. This project demonstrates a hierarchical multi-agent architecture, persistent database-backed memory, and multimodal intelligence, all deployed as a "Cloud Native" application on **Google Cloud Run** with **AlloyDB**.

## 🌟 Unique Features

- **Hierarchical Multi-Agent Team**: Moves beyond single-bot architectures. A central **Orchestrator** manager intelligently delegates tasks to a team of specialized sub-agents:
  - **TaskManager**: Database expert for AlloyDB operations.
  - **ScheduleManager**: Calendar and Notes specialist.
  - **MorningBriefer**: Cross-references tasks and schedules for daily planning.
  - **SafetyReviewer**: A dedicated guardrail agent that intercepts and reviews destructive actions (like deletions) for Responsible AI.
- **Infinite Memory (Persistent Sessions)**: Unlike standard chatbots that forget history on refresh, this system uses a `DatabaseSessionService` linked to **AlloyDB**. Your conversations and agent states are preserved permanently.
- **Vision-to-Task (Multimodal)**: Leverage Gemini 2.5/1.5 Flash's vision capabilities. Upload photos of handwritten notes, whiteboards, or lists, and the Orchestrator will automatically extract action items and save them to the database.
- **Cloud Native & Scalable**: Fully containerized for Google Cloud Run with **Direct VPC Egress** for secure, private communication with AlloyDB.

## 🏗️ Project Structure

```text
├── agents/              # Modular Agent Team
│   ├── orchestrator/    # Central Manager (Delegation Logic)
│   ├── task_manager/    # AlloyDB specialist
│   ├── schedule_manager/# Calendar & Notes specialist
│   ├── morning_briefer/ # Daily planning specialist
│   └── safety_reviewer/ # Guardrail & Compliance specialist
├── app/                 # Core Application Logic
│   ├── tools/
│   │   ├── db_tool.py   # SQLAlchemy + AlloyDB Connector logic
│   │   └── mcp_tools.py # MCP Service simulations (Calendar, Notes)
│   └── main.py          # FastAPI diagnostic endpoints
├── .adk.yaml            # ADK configuration for discovery
├── Dockerfile           # Optimized for Cloud Run
└── requirements.txt     # Python dependencies (ADK, SQLAlchemy, AlloyDB)
```

## 🚀 Setup & Local Development

1. **Clone and Navigate**:
   ```bash
   git clone https://github.com/SivaPanyam/GenAI-APAC-project.git
   cd GenAI-APAC-project
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_api_key
   CALENDAR_ENABLED=true
   NOTES_ENABLED=true
   ```
4. **Launch the Team**:
   The ADK will automatically discover the modular agents in the `agents/` directory.
   ```bash
   adk web agents/
   ```

## ☁️ Cloud Deployment (Google Cloud Run)

The system is designed for seamless deployment using `gcloud`.

### 1. Prerequisites
- Google Cloud Project with AlloyDB and Cloud Run APIs enabled.
- An AlloyDB instance residing in a VPC.

### 2. Deployment Command
```bash
gcloud run deploy multi-agent-assistant \
  --source . \
  --region us-central1 \
  --network=default \
  --subnet=default \
  --vpc-egress=private-ranges-only \
  --set-env-vars GOOGLE_API_KEY=your_key,ALLOYDB_INSTANCE_NAME=your_instance,DB_USER=postgres,DB_PASS=your_pass,DB_NAME=assistant_db,ADK_SESSION_SERVICE_URI=your_alloydb_uri
```

## 🛠️ Verification
- **ADK Web UI**: `https://your-service-url/`
- **Database Health**: `https://your-service-url/health/db`
- **Task List (JSON)**: `https://your-service-url/tasks`

---
*Built for the GenAI APAC Hackathon using Google ADK & Gemini.*
