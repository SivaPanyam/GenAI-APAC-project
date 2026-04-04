import sys
import uuid
from pathlib import Path
from typing import Generator
from fastapi import FastAPI
from pydantic import BaseModel

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent import get_runner
from google.genai import types

# Create FastAPI app
fastapi_app = FastAPI(title="Multi-Agent Assistant")

class UserRequest(BaseModel):
    message: str

def run_workflow_api(user_input: str):
    """Execution wrapper for the FastAPI chat endpoint."""
    runner = get_runner()
    
    # Generate unique IDs for this conversation
    user_id = "api_user"
    session_id = str(uuid.uuid4())
    
    # Create a Content object from the user input
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
    
    # Run the agent with proper parameters
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    )
    
    # Collect the response from event stream
    response_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
    
    return response_text if response_text else "No response from agent"

@fastapi_app.post("/chat")
def chat(request: UserRequest):
    """Chat endpoint for the multi-agent assistant"""
    response = run_workflow_api(request.message)
    return {"response": response}

@fastapi_app.get("/")
def root():
    """Welcome endpoint"""
    return {
        "message": "Multi-Agent Assistant is running!",
        "endpoints": {
            "chat": "POST /chat - Send a message to the assistant",
            "docs": "/docs - Interactive API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
