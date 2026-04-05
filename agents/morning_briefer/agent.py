import sys
from pathlib import Path
from google.adk import Agent

# Add parent directory to path to allow importing from 'app'
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tools.db_tool import retrieve_tasks
from app.tools.mcp_tools import calendar_tool

root_agent = Agent(
    name="MorningBriefer",
    instruction="""
    You are the Morning Briefing Specialist.
    Your job is to cross-reference the user's tasks and schedule to provide a daily summary or plan.
    - Call 'retrieve_tasks' to get their current task list from AlloyDB.
    - Call 'calendar_tool' with action 'view' to get their schedule.
    - Identify conflicts and suggest a productive plan for the day.
    """,
    model="gemini-2.5-flash", # Vertex AI compatible name
    tools=[retrieve_tasks, calendar_tool]
)
