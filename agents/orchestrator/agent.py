import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import sub-agents
from agents.task_manager.agent import root_agent as task_agent
from agents.schedule_manager.agent import root_agent as schedule_agent
from agents.safety_reviewer.agent import root_agent as safety_agent
from agents.morning_briefer.agent import root_agent as briefing_agent

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
    model="gemini-2.5-flash", # Vertex AI compatible name
    sub_agents=[
        task_agent, 
        schedule_agent, 
        safety_agent, 
        briefing_agent
    ] 
)
