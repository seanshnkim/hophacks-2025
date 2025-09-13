from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
from datetime import datetime
import json
from agent import learner_agent
from prompts import PROMPTS

# Initialize FastAPI app
app = FastAPI(
    title="HopHacks 2025 Learner API",
    description="AI-powered learning assistant API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LearnRequest(BaseModel):
    topic: str
    user_preferences: str = ""  # Single text field for user preferences

class LearnResponse(BaseModel):
    learning_module: str
    playground: Dict[str, Any]  # IPython notebook JSON
    topic: str
    timestamp: datetime

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }

# Learning endpoint
@app.post("/learn", response_model=LearnResponse)
async def learn(request: LearnRequest):
    """Get a learning response from the AI agent"""
    try:
        # Create system prompt for learning content
        learning_prompt = _create_learning_prompt(request.user_preferences)
        
        # Create user message
        user_message = f"I want to learn about: {request.topic}"
        
        # Agent call #1: Generate learning content
        learning_content = learner_agent.get_response(learning_prompt, [{"role": "user", "content": user_message}])
        
        # Agent call #2: Create notebook from learning content
        notebook_prompt = PROMPTS["notebook_creator"]
        notebook_input = f"Create a Jupyter notebook for these topics:\n\n{learning_content}\n\nReturn ONLY valid JSON with markdown and code cells."
        
        notebook_json_str = learner_agent.get_response(notebook_prompt, [{"role": "user", "content": notebook_input}])
        
        # Clean the response - remove markdown code blocks if present
        if notebook_json_str.strip().startswith('```json'):
            notebook_json_str = notebook_json_str.strip()[7:]  # Remove ```json
        if notebook_json_str.strip().endswith('```'):
            notebook_json_str = notebook_json_str.strip()[:-3]  # Remove ```
        notebook_json_str = notebook_json_str.strip()
        
        # Parse notebook JSON
        try:
            playground = json.loads(notebook_json_str)
            if "cells" not in playground:
                raise json.JSONDecodeError("Invalid notebook structure", notebook_json_str, 0)
        except json.JSONDecodeError as e:
            # Print error and content for debugging
            print(f"JSON Decode Error: {e}")
            print(f"Raw content: {notebook_json_str}")
            print("=" * 50)
            
            # If parsing fails, create a basic notebook structure
            playground = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "source": ["# Learning Module\n\n" + learning_content],
                        "metadata": {}
                    },
                    {
                        "cell_type": "code",
                        "source": ["# TODO: Implement the concepts from the learning module above"],
                        "metadata": {}
                    }
                ],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 2
            }
        
        return LearnResponse(
            learning_module=learning_content,
            playground=playground,
            topic=request.topic,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


def _create_learning_prompt(user_preferences: str) -> str:
    """Create learning prompt based on user preferences"""
    
    base_prompt = PROMPTS["learning_generator"]
    
    if user_preferences and user_preferences.strip():
        return f"""{base_prompt}

User Preferences: {user_preferences}

Please tailor your response to match these preferences as much as possible."""
    else:
        return base_prompt


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
