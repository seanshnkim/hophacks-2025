"""
Learning Blocks Module

Handles the creation and management of learning blocks for the new learning module approach.
Each block contains: id, topic, text content, and optional visualization path.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime
from agent import learner_agent, generate_visualization_video
from prompts import PROMPTS


@dataclass
class LearningBlock:
    """Represents a single learning block with topic, content, and visualization"""
    id: int
    topic: str
    text_content: str
    visualization_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "topic": self.topic,
            "text_content": self.text_content,
            "visualization_path": self.visualization_path
        }


class LearningBlockProcessor:
    """Processes topics into learning blocks with visualizations"""
    
    def __init__(self):
        self.visualizations_dir = "visualizations"
        self._ensure_visualizations_dir()
    
    def _ensure_visualizations_dir(self):
        """Create visualizations directory if it doesn't exist"""
        if not os.path.exists(self.visualizations_dir):
            os.makedirs(self.visualizations_dir)
    
    async def break_down_topic(self, topic: str) -> List[str]:
        """
        Break down a single topic into component subtopics using an agent call.
        """
        print(f"🔍 Breaking down topic: {topic}")
        
        # Use the topic breakdown prompt
        breakdown_prompt = PROMPTS["topic_breakdown"]
        user_message = f"Break down this topic into learnable components: {topic}"
        
        # Get breakdown from agent (no tools needed for this step)
        breakdown_response = await learner_agent.get_response(
            breakdown_prompt, 
            [{"role": "user", "content": user_message}], 
            tools=None
        )
        
        # Parse the response into a list of components
        components = self._parse_breakdown_response(breakdown_response)
        
        print(f"📋 Found {len(components)} components: {components}")
        return components
    
    def _parse_breakdown_response(self, response: str) -> List[str]:
        """Parse the breakdown response into a list of components"""
        components = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                # Remove any numbering or bullet points
                line = line.lstrip('0123456789.-* ').strip()
                if line:
                    components.append(line)
        
        return components
    
    def parse_topics(self, topics_input: str) -> List[str]:
        """
        Parse topics from string input into a list of individual topics.
        This is now used for backward compatibility with direct topic lists.
        """
        if not topics_input or not topics_input.strip():
            return []
        
        # Split by common delimiters
        topics = []
        
        # Try splitting by newlines first
        lines = topics_input.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Remove common list markers (1., 2., -, *, etc.)
                line = line.lstrip('0123456789.-* ').strip()
                if line:
                    topics.append(line)
        
        # If we only got one topic, try splitting by commas
        if len(topics) == 1 and ',' in topics[0]:
            topics = [topic.strip() for topic in topics[0].split(',') if topic.strip()]
        
        return topics
    
    async def process_topic(self, topic: str, topic_id: int, user_preferences: str = "") -> LearningBlock:
        """
        Process a single topic into a learning block with content and visualization.
        Includes retry mechanism for failed visualizations.
        """
        print(f"📚 Processing topic {topic_id}: {topic}")
        
        # Create system prompt for individual topic processing
        topic_prompt = self._create_topic_prompt(user_preferences)
        
        # Create user message for this specific topic
        user_message = f"Create learning content for this specific topic: {topic}"
        
        # Try up to 3 times for visualization generation
        max_retries = 3
        visualization_path = None
        clean_content = ""
        
        for attempt in range(max_retries):
            print(f"🔄 Attempt {attempt + 1}/{max_retries} for topic: {topic}")
            
            # Generate content with visualization tools
            learning_tools = [generate_visualization_video]
            content = await learner_agent.get_response(
                topic_prompt, 
                [{"role": "user", "content": user_message}], 
                tools=learning_tools
            )
            
            # Extract visualization path from tool results
            visualization_path = self._extract_visualization_path(content)
            
            # Check if visualization was successful
            if visualization_path:
                print(f"✅ Visualization successful on attempt {attempt + 1}")
                break
            else:
                # Check if there was a tool error
                tool_error = self._extract_tool_error(content)
                if tool_error and attempt < max_retries - 1:
                    print(f"❌ Visualization failed on attempt {attempt + 1}: {tool_error}")
                    print(f"🔄 Retrying with error feedback...")
                    
                    # Add error feedback to the user message for retry
                    user_message = f"Create learning content for this specific topic: {topic}\n\nPrevious attempt failed with error: {tool_error}\nPlease fix the Manim script and try again."
                else:
                    print(f"❌ Visualization failed after {attempt + 1} attempts")
                    break
        
        # Clean content (remove tool results section)
        clean_content = self._clean_content(content)
        
        return LearningBlock(
            id=topic_id,
            topic=topic,
            text_content=clean_content,
            visualization_path=visualization_path
        )
    
    def _create_topic_prompt(self, user_preferences: str) -> str:
        """Create prompt for processing individual topics"""
        base_prompt = """You are an expert learning assistant that creates detailed learning content for individual topics.

Your task is to create comprehensive learning content for the given topic.

Guidelines:
- Create detailed, educational content (not just headings)
- Explain concepts clearly with examples
- Make it engaging and easy to understand
- Include practical applications
- Adapt content based on user preferences

CRITICAL: For ANY topic involving visual concepts (graphs, functions, mathematical visualizations, charts, diagrams, etc.), you MUST call the generate_visualization_video tool to create actual Manim animations.

Available tools:
- generate_visualization_video(manim_script, scene_name): Create educational videos

When creating visualizations:
- Write complete Manim scripts with proper imports
- Use clear, educational animations
- Include explanatory text in the animations
- Make animations suitable for learning the concept
- Call the tool for each visual concept you identify
- NEVER use MathTex, Tex, get_graph_label, get_x_axis_label, get_y_axis_label, add_coordinates(), include_numbers=True, or NumberLine (requires LaTeX or has compatibility issues)
- ALWAYS use Text() instead of MathTex() for labels
- ALWAYS set axis_config={"include_numbers": False} for axes
- Use Text("label").next_to(object) instead of any label functions
- Create simple visualizations with basic shapes and Text labels only
- Use Axes() instead of NumberLine for coordinate systems

Create detailed, educational content that thoroughly covers the topic."""
        
        if user_preferences and user_preferences.strip():
            return f"""{base_prompt}

User Preferences: {user_preferences}

Please tailor your response to match these preferences as much as possible."""
        else:
            return base_prompt
    
    def _extract_visualization_path(self, content: str) -> Optional[str]:
        """Extract visualization path from tool results in content"""
        if "Tool Results:" in content:
            tool_section = content.split("Tool Results:")[1]
            if "Video generated successfully:" in tool_section:
                # Extract the path from the tool result
                lines = tool_section.strip().split('\n')
                for line in lines:
                    if "Video generated successfully:" in line:
                        # Extract path from line like "Video generated successfully: /path/to/video.mp4"
                        path = line.split("Video generated successfully:")[1].strip()
                        # Convert to relative path
                        if path.startswith(self.visualizations_dir):
                            return path.replace(self.visualizations_dir + "/", "")
                        return path
        return None
    
    def _extract_tool_error(self, content: str) -> Optional[str]:
        """Extract error information from tool results in content"""
        if "Tool Results:" in content:
            tool_section = content.split("Tool Results:")[1]
            if "Error generating video:" in tool_section:
                # Extract the error from the tool result
                lines = tool_section.strip().split('\n')
                for line in lines:
                    if "Error generating video:" in line:
                        # Extract error from line like "Error generating video: [error message]"
                        error = line.split("Error generating video:")[1].strip()
                        return error
        return None
    
    def _clean_content(self, content: str) -> str:
        """Remove tool results section from content"""
        if "Tool Results:" in content:
            return content.split("Tool Results:")[0].strip()
        return content
    
    async def process_single_topic(self, topic: str, user_preferences: str = "") -> List[LearningBlock]:
        """
        Process a single topic by breaking it down into components, then creating blocks for each component.
        """
        print(f"🎯 Processing single topic: {topic}")
        
        # Step 1: Break down the topic into components
        components = await self.break_down_topic(topic)
        
        if not components:
            print(f"❌ No components found for topic: {topic}")
            return []
        
        # Step 2: Process each component into a learning block
        blocks = []
        for i, component in enumerate(components, 1):
            try:
                block = await self.process_topic(component, i, user_preferences)
                blocks.append(block)
                print(f"✅ Completed component {i}/{len(components)}: {component}")
            except Exception as e:
                print(f"❌ Error processing component '{component}': {e}")
                # Create a basic block even if processing fails
                blocks.append(LearningBlock(
                    id=i,
                    topic=component,
                    text_content=f"Error processing this component: {str(e)}",
                    visualization_path=None
                ))
        
        return blocks
    
    async def process_topics(self, topics: List[str], user_preferences: str = "") -> List[LearningBlock]:
        """
        Process a list of topics into learning blocks.
        This is for backward compatibility with direct topic lists.
        """
        blocks = []
        
        for i, topic in enumerate(topics, 1):
            try:
                block = await self.process_topic(topic, i, user_preferences)
                blocks.append(block)
                print(f"✅ Completed topic {i}/{len(topics)}: {topic}")
            except Exception as e:
                print(f"❌ Error processing topic '{topic}': {e}")
                # Create a basic block even if processing fails
                blocks.append(LearningBlock(
                    id=i,
                    topic=topic,
                    text_content=f"Error processing this topic: {str(e)}",
                    visualization_path=None
                ))
        
        return blocks
    
    def save_blocks(self, blocks: List[LearningBlock], filename: str = None) -> str:
        """
        Save learning blocks to a JSON file for future reference.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"learning_blocks_{timestamp}.json"
        
        filepath = os.path.join(self.visualizations_dir, filename)
        
        # Create structured JSON data
        blocks_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_blocks": len(blocks),
                "version": "1.0"
            },
            "blocks": {}
        }
        
        # Map blocks by ID
        for block in blocks:
            blocks_data["blocks"][str(block.id)] = {
                "id": block.id,
                "title": block.topic,
                "text_content": block.text_content,
                "visualization_path": block.visualization_path
            }
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blocks_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Learning blocks saved to: {filepath}")
        return filepath
    
    def load_blocks(self, filepath: str) -> Dict[str, Any]:
        """
        Load learning blocks from a JSON file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                blocks_data = json.load(f)
            print(f"📂 Learning blocks loaded from: {filepath}")
            return blocks_data
        except Exception as e:
            print(f"❌ Error loading blocks from {filepath}: {e}")
            return {}


# Global processor instance
learning_processor = LearningBlockProcessor()
