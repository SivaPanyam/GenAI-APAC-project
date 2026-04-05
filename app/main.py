import sys
import uuid
import os
from pathlib import Path
from typing import Generator
from fastapi import FastAPI
from pydantic import BaseModel

# Add parent directory to path so we can import app modules
# This ensures that 'from app.agent import ...' works correctly
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.agent import get_runner
from app.tools.db_tool import test_db_connection, retrieve_tasks
from google.genai import types

# Create FastAPI app instance
app = FastAPI(title="Multi-Agent Assistant")

@app.get("/health/db")
def db_health():
    """Diagnostic endpoint to check AlloyDB connectivity."""
    return test_db_connection()

@app.get("/tasks")
def list_tasks():
    """Returns all tasks stored in the AlloyDB database."""
    return {"tasks": retrieve_tasks()}

class UserRequest(BaseModel):
    """Schema for incoming chat requests."""
    message: str

def run_workflow_api(user_input: str):
    """Execution wrapper for the FastAPI chat endpoint."""
    runner = get_runner()
    
    # Generate unique IDs for this conversation session
    user_id = "api_user"
    session_id = str(uuid.uuid4())
    
    # Create a Content object required by the Google GenAI SDK
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
    
    # Run the agent workflow and process the event stream
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    )
    
    # Collect and concatenate text parts from the event stream
    response_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if getattr(part, 'text', None):
                    response_text += part.text
    
    return response_text if response_text else "No response from agent"

@app.post("/chat")
def chat(request: UserRequest):
    """Endpoint to interact with the multi-agent assistant."""
    response = run_workflow_api(request.message)
    return {"response": response}

@app.get("/")
def root():
    """Health check and discovery endpoint."""
    return {
        "message": "Multi-Agent Assistant is running!",
        "status": "online",
        "endpoints": {
            "chat": "POST /chat - Send a message to the assistant",
            "docs": "/docs - Interactive API documentation (Swagger UI)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # CRITICAL FOR CLOUD RUN: 
    # Cloud Run injects a PORT environment variable. We must listen on it.
    # If the variable isn't found (local dev), it defaults to 8000.
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port,
        reload=False  # Set to True for local development only
    )