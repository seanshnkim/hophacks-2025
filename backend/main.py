from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
from datetime import datetime
from agent import learner_agent

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
    response: str
    topic: str
    timestamp: datetime

class ConversationHistory(BaseModel):
    messages: List[Dict[str, Any]]

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
        # Get response from agent
        response = learner_agent.get_response(
            topic=request.topic,
            user_preferences=request.user_preferences
        )
        
        return LearnResponse(
            response=response,
            topic=request.topic,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Get conversation history
@app.get("/conversation", response_model=ConversationHistory)
async def get_conversation():
    """Get the current conversation history"""
    try:
        messages = learner_agent.get_conversation_history()
        return ConversationHistory(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")

# Reset conversation
@app.post("/conversation/reset")
async def reset_conversation():
    """Reset the conversation history"""
    try:
        learner_agent.reset_conversation()
        return {"message": "Conversation reset successfully", "timestamp": datetime.now()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
