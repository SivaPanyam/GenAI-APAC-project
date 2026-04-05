import uuid
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.genai import types

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import custom tools
from app.tools.db_tool import save_to_database, retrieve_tasks, delete_task, get_conn
from app.tools.mcp_tools import calendar_tool, notes_tool

# -------------------------------------------------------------------------
# 1. SPECIALIZED SUB-AGENTS (The Team)
# -------------------------------------------------------------------------

# TASK AGENT
task_agent = Agent(
    name="TaskManager",
    instruction="""
    You are a database expert. Your job is to manage the user's tasks in AlloyDB.
    - To save a task: use 'save_to_database'.
    - To see tasks: use 'retrieve_tasks'.
    - To remove tasks: use 'delete_task'.
    Always confirm when a task has been successfully modified.
    """,
    model="gemini-2.5-flash",
    tools=[save_to_database, retrieve_tasks, delete_task]
)

# SCHEDULE AGENT
schedule_agent = Agent(
    name="ScheduleManager",
    instruction="""
    You are a scheduling assistant. Your job is to handle calendar events and quick notes.
    - For appointments/dates: use 'calendar_tool'.
    - For quick thoughts/memos: use 'notes_tool'.
    Be professional and organized.
    """,
    model="gemini-2.5-flash",
    tools=[calendar_tool, notes_tool]
)

# SAFETY AGENT
safety_agent = Agent(
    name="SafetyReviewer",
    instruction="""
    You are a Safety Guardrail. Your only job is to review proposed DELETION or DESTRUCTIVE actions.
    
    PROTOCOL:
    1. If the user wants to DELETE a task or event, check if they specified WHICH ONE.
    2. If it's clear, output: "APPROVED: This action is safe to proceed."
    3. If it's vague (e.g., 'delete everything'), output: "REJECTED: Please be more specific about what you want to delete."
    
    Do NOT execute tools yourself. Just provide the safety verdict.
    """,
    model="gemini-2.5-flash"
)

# BRIEFING AGENT
briefing_agent = Agent(
    name="MorningBriefer",
    instruction="""
    You are the Morning Briefing Specialist.
    Your job is to cross-reference the user's tasks and schedule to provide a daily summary or plan.
    - Call 'retrieve_tasks' to get their current task list from AlloyDB.
    - Call 'calendar_tool' with action 'view' to get their schedule.
    - Identify conflicts and suggest a productive plan for the day.
    """,
    model="gemini-2.5-flash",
    tools=[retrieve_tasks, calendar_tool]
)

# -------------------------------------------------------------------------
# 2. ROOT ORCHESTRATOR (The Manager)
# -------------------------------------------------------------------------

root_agent = Agent(
    name="Orchestrator",
    instruction="""
    You are the Manager of a Multi-Agent Assistant Team. 
    Your goal is to delegate user requests to the correct specialist.

    DELEGATION RULES:
    - For anything involving TASKS or DATABASE: Delegate to 'TaskManager'.
    - For anything involving CALENDAR or NOTES: Delegate to 'ScheduleManager'.
    - If the user asks for a morning brief, summary of their day, or planning: Delegate to 'MorningBriefer'.
    - CRITICAL SAFETY RULE: Before you let ANY agent DELETE something, you MUST consult the 'SafetyReviewer' first.
      Only if 'SafetyReviewer' says APPROVED can you proceed with the deletion.
      
    VISION-TO-TASK RULE:
    - If the user provides an image (e.g., a handwritten note, whiteboard, or list), analyze the image, extract the tasks or action items, and immediately delegate them to 'TaskManager' to be saved into the database.

    Stay in the Manager persona. Coordinate the team to help the user.
    """,
    model="gemini-2.5-flash",
    # Sub-agents must be passed in sub_agents
    sub_agents=[
        task_agent, 
        schedule_agent, 
        safety_agent, 
        briefing_agent
    ] 
)

# -------------------------------------------------------------------------
# 3. RUNNER CONFIGURATION
# -------------------------------------------------------------------------

try:
    if os.getenv("K_SERVICE"):
        session_service = DatabaseSessionService("postgresql+pg8000://", creator=get_conn)
    else:
        session_service = InMemorySessionService()
except Exception:
    session_service = InMemorySessionService()

app_runner = Runner(
    app_name="MultiAgentAssistant",
    agent=root_agent,
    session_service=session_service,
    auto_create_session=True
)

def get_runner(app_name="MultiAgentAssistant"):
    return app_runner

def run_workflow(user_input: str):
    runner = get_runner()
    user_id = "default_user"
    session_id = str(uuid.uuid4())
    message = types.Content(role="user", parts=[types.Part(text=user_input)])
    events = runner.run(user_id=user_id, session_id=session_id, new_message=message)
    
    response_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if getattr(part, 'text', None):
                    response_text += part.text
    return response_text if response_text else "No response from agent"
