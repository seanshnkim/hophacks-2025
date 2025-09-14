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
        Process a single topic into a learning block using two-step approach:
        1. Generate text content (no tools)
        2. Generate visualization based on text content (if appropriate)
        """
        print(f"📚 Processing topic {topic_id}: {topic}")
        
        # Step 1: Generate text content (no tools)
        text_content = await self._generate_text_content(topic, user_preferences)
        
        # Step 2: Generate visualization based on text content (if appropriate)
        visualization_path = await self._generate_visualization(topic, text_content)
        
        return LearningBlock(
            id=topic_id,
            topic=topic,
            text_content=text_content,
            visualization_path=visualization_path
        )
    
    async def _generate_text_content(self, topic: str, user_preferences: str = "") -> str:
        """Generate detailed text content for the topic (no tools)"""
        print(f"📝 Generating text content for: {topic}")
        
        text_prompt = self._create_text_prompt(user_preferences)
        user_message = f"Create comprehensive learning content for this specific topic: {topic}"
        
        # Generate content without tools to focus on text
        content = await learner_agent.get_response(
            text_prompt, 
            [{"role": "user", "content": user_message}], 
            tools=None
        )
        
        # Ensure content is a string
        if isinstance(content, list):
            content = '\n'.join(str(item) for item in content)
        
        # Clean and validate content
        content = str(content).strip()
        
        # Check if content is too long and needs trimming
        word_count = len(content.split())
        if word_count > 250:  # Allow some buffer above 200 word limit
            print(f"⚠️ Content too long ({word_count} words), trimming for '{topic}'")
            # Keep only the first 200 words
            words = content.split()[:200]
            content = ' '.join(words) + "..."
        
        # Fallback: If no content was generated, create a basic explanation
        if not content:
            content = f"# {topic}\n\nEssential concepts for {topic.lower()}. Research this topic further for detailed information."
            print(f"⚠️ No text content generated for '{topic}', using fallback content")
        else:
            final_word_count = len(content.split())
            print(f"✅ Generated {len(content)} characters ({final_word_count} words) of text content for '{topic}'")
        
        return content
    
    async def _generate_visualization(self, topic: str, text_content: str) -> Optional[str]:
        """Generate visualization based on text content (if appropriate) with retry logic"""
        print(f"🎨 Considering visualization for: {topic}")
        
        viz_prompt = self._create_visualization_prompt()
        user_message = f"""Analyze this topic to determine if it would benefit from visual representation to show logic/setup intuitively:

Topic: "{topic}"

Text Content:
{text_content}

ANALYSIS QUESTIONS:
1. Is this topic about logical relationships, processes, or structures?
2. Would a visual diagram, flowchart, or animation help explain this concept?
3. Is this topic about relationships, processes, structures, or logical flow?
4. Would "showing" this concept be more effective than just "telling" about it?

If this topic involves:
- Data structures, algorithms, or mathematical concepts
- Logical systems, processes, or workflows
- Spatial relationships, hierarchies, or connections
- Abstract concepts that can be visualized
- Step-by-step procedures or transformations

Then create a Manim animation that:
- Shows the logical structure or flow
- Illustrates relationships between components
- Demonstrates processes step-by-step
- Makes abstract concepts concrete and visual

Use the generate_visualization_video tool to create the animation."""
        
        # Retry logic for visualization generation
        max_retries = 3
        learning_tools = [generate_visualization_video]
        
        for attempt in range(1, max_retries + 1):
            print(f"🎨 Visualization attempt {attempt}/{max_retries} for topic: {topic}")
            
            try:
                # Generate visualization with tools
                content = await learner_agent.get_response(
                    viz_prompt, 
                    [{"role": "user", "content": user_message}], 
                    tools=learning_tools
                )
                
                # Extract visualization path from tool results
                visualization_path = self._extract_visualization_path(content)
                
                # Check if there was a tool error
                tool_error = self._extract_tool_error(content)
                
                if tool_error:
                    print(f"❌ Visualization attempt {attempt} failed: {tool_error}")
                    if attempt < max_retries:
                        print(f"🔄 Retrying visualization for topic: {topic}")
                        import asyncio
                        await asyncio.sleep(2)  # Wait 2 seconds before retry
                        continue
                    else:
                        print(f"❌ All visualization attempts failed for topic: {topic}")
                        return None
                elif visualization_path:
                    print(f"✅ Visualization created for topic: {topic} (attempt {attempt})")
                    return visualization_path
                else:
                    print(f"ℹ️ No visualization created for topic: {topic} - AI determined it's not needed")
                    return None
                    
            except Exception as e:
                print(f"❌ Visualization attempt {attempt} error: {str(e)}")
                if attempt < max_retries:
                    print(f"🔄 Retrying visualization for topic: {topic}")
                    import asyncio
                    await asyncio.sleep(2)  # Wait 2 seconds before retry
                    continue
                else:
                    print(f"❌ All visualization attempts failed for topic: {topic}")
                    return None
        
        return None
    
    def _create_text_prompt(self, user_preferences: str) -> str:
        """Create prompt focused on text content generation (no tools)"""
        base_prompt = """You are an expert learning assistant that creates CONCISE, focused learning content.

TASK: Create brief educational text (MAX 200 words) that explains the topic efficiently.

REQUIRED FORMAT:
- Use markdown headings (##, ###)
- Bullet points for key concepts
- Brief examples only
- No fluff or rambling

CONTENT REQUIREMENTS:
- Core concept explanation (1-2 sentences)
- Key points (bullet list)
- 1 practical example
- Essential applications only

STRICT GUIDELINES:
- MAX 200 words total
- Be direct and to the point
- No repetitive explanations
- No filler words or phrases
- Focus on actionable information
- Use simple, clear language
- Get to the point quickly

Create focused content that teaches effectively in minimal words."""
        
        if user_preferences and user_preferences.strip():
            base_prompt += f"\n\nUser Preferences: {user_preferences}"
        
        return base_prompt
    
    def _create_visualization_prompt(self) -> str:
        """Create prompt focused on visualization generation based on text content"""
        return """You are an expert at creating educational visualizations using Manim.

Your task is to analyze topics and determine if they would benefit from visual representation to show logic/setup intuitively.

ANALYSIS CRITERIA - CREATE VISUALIZATIONS FOR TOPICS THAT ARE:
1. LOGICAL/CONCEPTUAL: Topics that involve logical relationships, processes, or structures
2. VISUAL BY NATURE: Concepts that are inherently spatial, geometric, or diagrammatic
3. PROCESS-ORIENTED: Step-by-step procedures, workflows, or transformations
4. RELATIONSHIP-BASED: Concepts involving connections, hierarchies, or dependencies
5. ABSTRACT BUT VISUALIZABLE: Complex ideas that can be simplified through visual representation

STRONG CANDIDATES FOR VISUALIZATION:
- Data structures (arrays, trees, graphs, linked lists, stacks, queues, hash tables)
- Algorithms (sorting, searching, traversal, data structure operations)
- Mathematical concepts (functions, graphs, equations, geometric shapes, vectors, matrices)
- Logical systems (boolean logic, decision trees, flowcharts)
- Scientific processes (step-by-step procedures, transformations, cycles)
- Spatial relationships (hierarchies, connections, flows, networks)
- Abstract concepts that involve structure, organization, or systematic thinking
- Any topic where "showing" the concept would be more effective than just "telling"

WEAK CANDIDATES (usually don't need visualization):
- Pure text-based topics (writing, literature, history)
- Memorization-heavy subjects (vocabulary, facts, dates)
- Topics that are purely theoretical without practical application
- Simple definitions or explanations that don't involve relationships or processes

DECISION PROCESS:
1. Analyze the topic name and text content
2. Ask: "Would a visual diagram, flowchart, or animation help explain this concept?"
3. Ask: "Is this topic about relationships, processes, structures, or logical flow?"
4. If YES to either question, create a visualization
5. If NO to both questions, skip visualization

When creating visualizations, focus on:
- Showing the logical structure or flow
- Illustrating relationships between components
- Demonstrating processes step-by-step
- Making abstract concepts concrete and visual

When creating visualizations, follow these STRICT rules to avoid errors:

1. MANIM SCRIPT STRUCTURE:
   - Always start with: from manim import *
   - Always define a class that inherits from Scene
   - Always have a construct() method
   - Use proper indentation (4 spaces)

2. FORBIDDEN METHODS/OBJECTS (will cause errors):
   - NEVER use: MathTex, Tex, NumberLine, get_graph_label, get_x_axis_label, get_y_axis_label, add_coordinates()
   - NEVER use: add_coordinate_labels() - this method doesn't exist, use Text() labels instead
   - NEVER use: Image() - not available, use Text() or other basic shapes instead
   - NEVER use: align_left, align_right, align_center - these methods don't exist on Text objects
   - NEVER use: include_numbers=True, dx_color, stroke_width, add_brackets, add_row_indices parameters
   - NEVER use: get_end_point() - use get_end() instead
   - NEVER use: get_tangent_line() - not available in this version
   - NEVER use: get_vertical_line_graph() - not available in this version
   - NEVER use: get_area() with x_range parameters - use different approach
   - NEVER use: coords_to_point() for animations - use Dot() instead
   - NEVER use: Matrix() with complex parameters - use Text() instead
   - NEVER use: Table() with add_row_indices or other complex parameters - use Text() instead
   - NEVER use: plot_arrow_from_origin_to_coords() - not available in this version
   - NEVER use: get_vector() with color parameter - use Arrow() instead
   - NEVER use: any method with unexpected keyword arguments
   - NEVER use: any complex mathematical objects that require LaTeX

3. REQUIRED PATTERNS:
   - ALWAYS use Text() for all labels and text
   - ALWAYS set axis_config={"include_numbers": False} for Axes
   - ALWAYS use .animate for animations, never pass methods to self.play()
   - ALWAYS use Axes() instead of NumberLine for coordinate systems
   - ALWAYS use proper method calls: axes.x_axis.get_end() not get_end_point()

4. CORRECT ANIMATION PATTERNS:
   - Use: self.play(Create(object)) for creating objects
   - Use: self.play(Write(text)) for text
   - Use: self.play(object.animate.set_color(COLOR)) for color changes
   - Use: self.play(object.animate.move_to(position)) for movement
   - Use: self.play(FadeOut(object)) for removing objects

5. SIMPLE EXAMPLE TEMPLATES:

For any topic, you can create simple visualizations like:

```python
from manim import *

class SimpleConceptScene(Scene):
    def construct(self):
        # Simple text-based visualization
        title = Text("Topic Name").to_edge(UP)
        self.play(Write(title))
        
        # Key points
        point1 = Text("Key Point 1").next_to(title, DOWN, buff=1)
        point2 = Text("Key Point 2").next_to(point1, DOWN, buff=0.5)
        point3 = Text("Key Point 3").next_to(point2, DOWN, buff=0.5)
        
        self.play(Write(point1))
        self.wait(0.5)
        self.play(Write(point2))
        self.wait(0.5)
        self.play(Write(point3))
        self.wait(1)
```

```python
from manim import *

class SimpleDiagramScene(Scene):
    def construct(self):
        # Simple diagram
        title = Text("Concept Diagram").to_edge(UP)
        self.play(Write(title))
        
        # Create simple shapes
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=1.5, color=RED).next_to(circle, RIGHT, buff=1)
        
        # Add labels
        circle_label = Text("A").move_to(circle)
        square_label = Text("B").move_to(square)
        
        # Animate
        self.play(Create(circle), Write(circle_label))
        self.wait(0.5)
        self.play(Create(square), Write(square_label))
        self.wait(1)
```

6. COMMON FIXES:
   - For vectors: Use Arrow(start_point, end_point) instead of axes.get_vector() or axes.plot_arrow_from_origin_to_coords()
   - For matrices: Use Text() with proper formatting instead of Matrix() or Table()
   - For areas: Use Polygon() with calculated points instead of get_area()
   - For animations: Always use .animate, never pass methods directly
   - For arrows: Use Arrow(start_point, end_point) instead of axes methods
   - For tables: Use Text() with newlines instead of Table()
   - For mathematical expressions: Use Text() instead of MathTex() or Tex()
   - For coordinate systems: Use Axes() instead of NumberLine()
   - For coordinate labels: Use Text() positioned manually instead of add_coordinate_labels()
   - For images: Use Text() or basic shapes instead of Image()
   - For text alignment: Use .to_edge(LEFT/RIGHT/UP/DOWN) instead of align_left/align_right

7. ERROR PREVENTION:
   - Test all method calls before using them
   - Use simple, basic Manim objects only
   - Avoid complex mathematical operations in Manim
   - Keep animations simple and educational
   - Always include self.wait() for timing
   - When in doubt, use Text() for any mathematical content

Available tools:
- generate_visualization_video(manim_script, scene_name): Create educational videos

Create a Manim script and call the generate_visualization_video tool to help students understand this topic better."""
    
    
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
