#!/usr/bin/env python
"""
Command-line interface for the Multi-Agent Assistant
"""
import sys
import uuid
from pathlib import Path
from typing import Generator

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent import get_runner
from google.genai import types

def chat_cli(user_input: str):
    """Send a message to the agent and get a response"""
    user_id = "cli_user"
    session_id = str(uuid.uuid4())
    
    runner = get_runner()
    
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

def main():
    """Main CLI loop"""
    print("=" * 60)
    print("Multi-Agent Assistant - CLI Mode")
    print("=" * 60)
    print("Type your message and press Enter. Type 'exit' or 'quit' to exit.")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            print("\nAgent: Thinking...", end="\r")
            response = chat_cli(user_input)
            print(f"Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
