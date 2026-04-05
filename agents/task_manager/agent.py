import sys
from pathlib import Path
from google.adk import Agent

# Add parent directory to path to allow importing from 'app'
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tools.db_tool import save_to_database, retrieve_tasks, delete_task

root_agent = Agent(
    name="TaskManager",
    instruction="""
    You are a database expert. Your job is to manage the user's tasks in AlloyDB.
    - To save a task: use 'save_to_database'.
    - To see tasks: use 'retrieve_tasks'.
    - To remove tasks: use 'delete_task'.
    Always confirm when a task has been successfully modified.
    """,
    model="gemini-2.5-flash", # Vertex AI compatible name
    tools=[save_to_database, retrieve_tasks, delete_task]
)
