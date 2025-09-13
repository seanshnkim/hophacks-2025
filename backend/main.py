from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
from datetime import datetime
import json
import os
from learning_blocks import learning_processor, LearningBlock
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
    topic: str  # Single topic to break down into components
    user_preferences: str = ""  # Single text field for user preferences

class LearningBlockResponse(BaseModel):
    id: int
    topic: str
    text_content: str
    visualization_path: Optional[str] = None

class LearnResponse(BaseModel):
    learning_blocks: List[LearningBlockResponse]  # List of learning blocks
    playground: Dict[str, Any]  # IPython notebook JSON
    main_topic: str  # The original topic that was broken down
    components: List[str]  # List of component subtopics
    timestamp: datetime

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }

# Visualization endpoint
@app.get("/visualization/{visualization_path:path}")
async def get_visualization(visualization_path: str):
    """Serve MP4 visualization files"""
    # Construct the full path to the visualization file
    full_path = os.path.join("visualizations", visualization_path)
    
    # Check if file exists
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Visualization file not found")
    
    # Check if it's an MP4 file
    if not visualization_path.lower().endswith('.mp4'):
        raise HTTPException(status_code=400, detail="File is not an MP4 video")
    
    # Return the file
    return FileResponse(
        path=full_path,
        media_type="video/mp4",
        filename=os.path.basename(visualization_path)
    )

# Learning endpoint
@app.post("/learn", response_model=LearnResponse)
async def learn(request: LearnRequest):
    """Get a learning response from the AI agent using the new topic breakdown approach"""
    try:
        print(f"📚 Processing learning request with topic: {request.topic}")
        
        # Process single topic by breaking it down into components
        learning_blocks = await learning_processor.process_single_topic(request.topic, request.user_preferences)
        
        if not learning_blocks:
            raise HTTPException(status_code=400, detail="No learning components could be generated for this topic")
        
        # Check if too many components failed (more than 50% failed)
        failed_components = sum(1 for block in learning_blocks if not block.text_content.strip())
        total_components = len(learning_blocks)
        
        if failed_components > total_components * 0.5:
            raise HTTPException(
                status_code=500, 
                detail=f"Too many components failed to generate content ({failed_components}/{total_components}). Please try a different topic or check the system logs."
            )
        
        # Extract components list from blocks
        components = [block.topic for block in learning_blocks]
        
        print(f"📋 Generated {len(learning_blocks)} learning blocks from topic: {request.topic}")
        print(f"🔧 Components: {components}")
        
        # Save blocks to file for future reference
        blocks_file = learning_processor.save_blocks(learning_blocks)
        print(f"💾 Learning blocks saved to: {blocks_file}")
        
        # Create playground from learning blocks
        playground = _create_playground_from_blocks(learning_blocks)
        
        # Convert blocks to response format
        block_responses = [
            LearningBlockResponse(
                id=block.id,
                topic=block.topic,
                text_content=block.text_content,
                visualization_path=block.visualization_path
            )
            for block in learning_blocks
        ]
        
        return LearnResponse(
            learning_blocks=block_responses,
            playground=playground,
            main_topic=request.topic,
            components=components,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        print(f"❌ Error in learn endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


def _create_playground_from_blocks(learning_blocks: List[LearningBlock]) -> Dict[str, Any]:
    """Create a Jupyter notebook playground from learning blocks"""
    
    cells = []
    
    # Add introduction cell
    cells.append({
        "cell_type": "markdown",
        "source": ["# Learning Module\n\nThis notebook contains learning components for the following topics:\n\n" + 
                  "\n".join([f"- {block.topic}" for block in learning_blocks])],
        "metadata": {}
    })
    
    # Add a cell for each learning block
    for block in learning_blocks:
        # Markdown cell with component and content
        cells.append({
            "cell_type": "markdown",
            "source": [f"## Component {block.id}: {block.topic}\n\n{block.text_content}"],
            "metadata": {}
        })
        
        # Code cell for exercises
        cells.append({
            "cell_type": "code",
            "source": [f"# TODO: Implement exercises for {block.topic}\n# Add your code here\n# Example: variable_name = 'hello'"],
            "metadata": {}
        })
    
    return {
        "cells": cells,
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
