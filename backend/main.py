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
    topic: str  # Single topic to break down into components
    user_preferences: str = ""  # Single text field for user preferences

class LearningBlockResponse(BaseModel):
    id: int
    topic: str
    text_content: str
    visualization_path: Optional[str] = None

class LearnResponse(BaseModel):
    learning_blocks: List[LearningBlockResponse]  # List of learning blocks
    playground_path: str  # Path to the saved .ipynb file
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
        # Count as failed if there's no text content AND no visualization (complete failure)
        failed_components = sum(1 for block in learning_blocks if not block.text_content.strip() and not block.visualization_path)
        total_components = len(learning_blocks)
        
        # Debug: Print details about each block
        print(f"🔍 Component status summary:")
        for i, block in enumerate(learning_blocks):
            has_text = bool(block.text_content.strip())
            has_viz = bool(block.visualization_path)
            status = "✅ OK" if (has_text or has_viz) else "❌ FAILED"
            print(f"  Component {i+1}: {block.topic} - Text: {has_text}, Viz: {has_viz} - {status}")
        
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
        
        # Create playground from learning blocks and save as .ipynb file
        try:
            playground = await _create_playground_with_llm(learning_blocks, request.topic)
            playground_path = _save_playground_as_notebook(playground, request.topic)
            print(f"✅ Playground created and saved: {playground_path}")
        except Exception as e:
            print(f"❌ Error creating playground: {str(e)}")
            playground_path = "error_creating_notebook.ipynb"
        
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
            playground_path=playground_path,
            main_topic=request.topic,
            components=components,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        print(f"❌ Error in learn endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


async def _create_playground_with_llm(learning_blocks: List[LearningBlock], main_topic: str) -> Dict[str, Any]:
    """Create a Jupyter notebook using LLM to generate the complete JSON structure"""
    
    print(f"🤖 Generating notebook with LLM for topic: {main_topic}")
    
    # Extract component topics
    component_topics = [block.topic for block in learning_blocks]
    
    # Create prompt for notebook generation
    notebook_prompt = PROMPTS["notebook_creator"]
    user_message = f"""Create a Jupyter notebook for this learning module:

Main Topic: {main_topic}

Component Topics:
{chr(10).join([f"- {topic}" for topic in component_topics])}

For each component topic, create:
1. A markdown cell explaining the concept and what to learn
2. A code cell with practical exercises and examples

Make it educational and hands-on with real Python code examples."""
    
    try:
        # Generate notebook JSON using LLM with timeout handling
        import asyncio
        try:
            notebook_json = await asyncio.wait_for(
                learner_agent.get_response(
                    notebook_prompt,
                    [{"role": "user", "content": user_message}],
                    tools=None
                ),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            print(f"⏰ LLM timeout for notebook generation, using ultra-simple fallback")
            component_topics = [block.topic for block in learning_blocks]
            return _create_ultra_simple_notebook(component_topics, main_topic)
        
        print(f"🔍 Raw LLM response length: {len(notebook_json)} characters")
        
        # Clean the response to extract pure JSON
        cleaned_json = _clean_json_response(notebook_json)
        
        # Parse the JSON response
        try:
            notebook = json.loads(cleaned_json)
            print(f"✅ Successfully parsed notebook JSON with {len(notebook.get('cells', []))} cells")
            return notebook
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"🔍 Raw response: {notebook_json[:500]}...")
            print(f"🔍 Cleaned response: {cleaned_json[:500]}...")
            # Fallback to ultra-simple notebook structure
            component_topics = [block.topic for block in learning_blocks]
            return _create_ultra_simple_notebook(component_topics, main_topic)
            
    except Exception as e:
        print(f"❌ Error generating notebook with LLM: {str(e)}")
        # Fallback to ultra-simple notebook structure
        component_topics = [block.topic for block in learning_blocks]
        return _create_ultra_simple_notebook(component_topics, main_topic)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract pure JSON"""
    response = response.strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]  # Remove ```json
    elif response.startswith("```"):
        response = response[3:]  # Remove ```
    
    if response.endswith("```"):
        response = response[:-3]  # Remove trailing ```
    
    # Find the first { and last } to extract JSON
    start_idx = response.find('{')
    end_idx = response.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        response = response[start_idx:end_idx + 1]
    
    return response.strip()


def _create_simple_fallback_notebook(learning_blocks: List[LearningBlock], main_topic: str) -> Dict[str, Any]:
    """Create a simple fallback notebook if LLM generation fails"""
    
    cells = []
    
    # Add introduction cell
    cells.append({
        "cell_type": "markdown",
        "source": [f"# {main_topic}\n\nThis notebook contains learning components for the following topics:\n\n" + 
                  "\n".join([f"- {block.topic}" for block in learning_blocks])],
        "metadata": {}
    })
    
    # Add a cell for each learning block
    for block in learning_blocks:
        # Markdown cell with component and content
        cells.append({
            "cell_type": "markdown",
            "source": [f"## {block.topic}\n\n{block.text_content}"],
            "metadata": {}
        })
        
        # Simple code cell with basic template
        code_template = f"""# Exercise: {block.topic}
# Implement your solution here based on the learning content above

# TODO: Add your code here
def solve_problem():
    # Your code here
    pass

# Test your solution
# result = solve_problem()
# print(f"Result: {{result}}")"""
        
        cells.append({
            "cell_type": "code",
            "source": [code_template],
            "metadata": {
                "execution_count": None,
                "outputs": []
            },
            "execution_count": None,
            "outputs": []
        })
    
    # Create proper IPython notebook structure
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            },
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    return notebook


def _create_ultra_simple_notebook(component_topics: List[str], main_topic: str) -> Dict[str, Any]:
    """Create an ultra-simple notebook without LLM calls for maximum reliability"""
    
    cells = []
    
    # Add introduction cell
    cells.append({
        "cell_type": "markdown",
        "source": [f"# {main_topic}\n\nLearning notebook covering these topics:\n\n" + 
                  "\n".join([f"- {topic}" for topic in component_topics])],
        "metadata": {}
    })
    
    # Add a simple cell for each topic
    for i, topic in enumerate(component_topics, 1):
        # Markdown cell
        cells.append({
            "cell_type": "markdown",
            "source": [f"## {i}. {topic}\n\nLearn about {topic.lower()} concepts and implementation."],
            "metadata": {}
        })
        
        # Code cell
        cells.append({
            "cell_type": "code",
            "source": [f"# {topic} Exercise\n# Add your code here\n\nprint('Working on {topic}')"],
            "metadata": {"execution_count": None, "outputs": []},
            "execution_count": None,
            "outputs": []
        })
    
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.8.0"}
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }




def _save_playground_as_notebook(playground: Dict[str, Any], topic: str) -> str:
    """Save playground as proper .ipynb file and return the relative path"""
    # Create notebooks directory if it doesn't exist
    notebooks_dir = "notebooks"
    if not os.path.exists(notebooks_dir):
        os.makedirs(notebooks_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_')
    filename = f"playground_{safe_topic}_{timestamp}.ipynb"
    filepath = os.path.join(notebooks_dir, filename)
    
    # Validate notebook structure before saving
    if not _validate_notebook_structure(playground):
        print(f"⚠️ Warning: Notebook structure validation failed for {filename}")
    
    # Save the notebook with proper formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(playground, f, indent=2, ensure_ascii=False)
    
    print(f"📓 IPython notebook saved: {filepath}")
    print(f"📊 Notebook contains {len(playground.get('cells', []))} cells")
    return filename  # Return just the filename for the API response


def _validate_notebook_structure(notebook: Dict[str, Any]) -> bool:
    """Validate that the notebook has proper IPython structure"""
    try:
        # Check required top-level keys
        required_keys = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        if not all(key in notebook for key in required_keys):
            print(f"❌ Missing required keys: {[k for k in required_keys if k not in notebook]}")
            return False
        
        # Check nbformat version
        if notebook.get('nbformat') != 4:
            print(f"❌ Invalid nbformat version: {notebook.get('nbformat')}")
            return False
        
        # Check cells structure
        cells = notebook.get('cells', [])
        if not isinstance(cells, list):
            print("❌ Cells must be a list")
            return False
        
        for i, cell in enumerate(cells):
            if not isinstance(cell, dict):
                print(f"❌ Cell {i} is not a dictionary")
                return False
            
            if 'cell_type' not in cell:
                print(f"❌ Cell {i} missing cell_type")
                return False
            
            if cell['cell_type'] not in ['markdown', 'code', 'raw']:
                print(f"❌ Cell {i} has invalid cell_type: {cell['cell_type']}")
                return False
        
        # Check metadata structure
        metadata = notebook.get('metadata', {})
        if 'kernelspec' not in metadata:
            print("⚠️ Missing kernelspec in metadata")
        
        print("✅ Notebook structure validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating notebook structure: {e}")
        return False


# Notebook endpoint
@app.get("/notebook/{filename}")
async def get_notebook(filename: str):
    """Serve .ipynb notebook files"""
    # Construct the full path to the notebook file
    full_path = os.path.join("notebooks", filename)
    
    # Check if file exists
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Notebook file not found")
    
    # Check if it's an .ipynb file
    if not filename.lower().endswith('.ipynb'):
        raise HTTPException(status_code=400, detail="File is not a Jupyter notebook")
    
    # Return the file
    return FileResponse(
        path=full_path,
        media_type="application/json",
        filename=filename
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
