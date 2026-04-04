import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import custom tools
from app.tools.db_tool import save_to_database, retrieve_tasks
from app.tools.mcp_tools import calendar_tool, notes_tool

# Define the list of tools the agent can access
tools_list = [save_to_database, retrieve_tasks, calendar_tool, notes_tool]

# Initialize the Session Service (Global instance)
session_service = InMemorySessionService()

# Define the Agent Instance as root_agent
# The ADK specifically looks for an 'Agent' instance named 'root_agent'
root_agent = Agent(
    name="Orchestrator",
    instruction="""
    You are a highly capable Multi-Agent AI System Orchestrator. 
    Your goal is to help users manage tasks, schedules, and information.

    CORE PROTOCOL:
    1. PLAN: Analyze the user's request and break it into logical steps.
    2. EXECUTE: Call the appropriate tools (calendar_tool, save_to_database, etc.) for each step.
    3. SELF-CORRECT: Before providing a final answer, verify that the tool outputs actually fulfill the user's request.
    
    CAPABILITIES:
    - If the user mentions dates or times, use 'calendar_tool'.
    - If the user wants to save or remember a task long-term, use 'save_to_database'.
    - If the user asks for a summary of their current load, use 'retrieve_tasks'.

    Be concise, helpful, and confirm which actions were taken.
    """,
    model="gemini-flash-latest", # Using gemini-flash-latest for reliability and discovery compatibility
    tools=tools_list 
)

# Create a global runner instance with the agent
app_runner = Runner(
    app_name="MultiAgentAssistant",
    agent=root_agent,
    session_service=session_service,
    auto_create_session=True
)

def get_runner(app_name="MultiAgentAssistant"):
    """Returns the global configured ADK Runner instance."""
    return app_runner

def run_workflow(user_input: str):
    """Execution wrapper for the agent workflow."""
    runner = get_runner()
    
    # Generate unique IDs for this turn
    user_id = "default_user"
    session_id = str(uuid.uuid4())
    
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
    
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    )
    
    response_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
    
    return response_text if response_text else "No response from agent"
