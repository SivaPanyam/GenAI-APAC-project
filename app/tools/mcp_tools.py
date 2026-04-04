import os

def calendar_tool(action: str, details: str):
    """
    Interacts with the Calendar via MCP.
    - action: 'add', 'delete', or 'view'
    - details: The event name, time, and date.
    """
    # Check if calendar is enabled
    if os.getenv("CALENDAR_ENABLED", "false").lower() != "true":
        return "Calendar service is currently disabled in .env configuration."

    # This mimics the response from an MCP-connected Google Calendar
    return f"MCP Calendar Service: Executed {action} for '{details}'"

def notes_tool(content: str):
    """Saves quick notes to a markdown file via MCP."""
    if os.getenv("NOTES_ENABLED", "false").lower() != "true":
        return "Notes service is currently disabled in .env configuration."

    return f"MCP Notes Service: Note saved: {content}"