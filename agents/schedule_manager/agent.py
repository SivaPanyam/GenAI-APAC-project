import sys
from pathlib import Path
from google.adk import Agent

# Add parent directory to path to allow importing from 'app'
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tools.mcp_tools import calendar_tool, notes_tool

root_agent = Agent(
    name="ScheduleManager",
    instruction="""
    You are a scheduling assistant. Your job is to handle calendar events and quick notes.
    - For appointments/dates: use 'calendar_tool'.
    - For quick thoughts/memos: use 'notes_tool'.
    Be professional and organized.
    """,
    model="gemini-2.5-flash", # Vertex AI compatible name
    tools=[calendar_tool, notes_tool]
)
