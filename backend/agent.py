from typing import List, Dict, Any
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from configs import config
from tools import visualization_tools
import asyncio

@tool
async def generate_visualization_video(manim_script: str, scene_name: str = "Scene") -> str:
    """Generate a visualization video from a Manim script for educational content"""
    result = await visualization_tools.generate_visualization_video(manim_script, scene_name)
    
    if result["success"]:
        return f"Video generated successfully: {result['video_path']}"
    else:
        return f"Error generating video: {result['error']}"

class LearnerAgent:
    """Learning agent using Gemini Flash 2.5 with visualization tools"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Initialize the language model with config parameters
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )
    
    async def get_response(self, system_prompt: str, messages: List[Dict[str, str]], tools: List = None) -> str:
        """Get a response from the agent given a system prompt and message history"""
        
        # Prepare messages for the LLM
        llm_messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in messages:
            if msg["role"] == "user":
                llm_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                llm_messages.append(AIMessage(content=msg["content"]))
        
        # Get response from LLM with or without tools
        if tools:
            response = self.llm.invoke(llm_messages, tools=tools)
            
            # Check if the response contains tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tool calls detected: {len(response.tool_calls)} calls")
                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    print(f"🔧 Executing tool: {tool_call['name']}")
                    if tool_call['name'] == 'generate_visualization_video':
                        # Call the tool function directly instead of using LangChain's tool calling
                        result = await generate_visualization_video.ainvoke({
                            'manim_script': tool_call['args']['manim_script'],
                            'scene_name': tool_call['args'].get('scene_name', 'Scene')
                        })
                        tool_results.append(result)
                        print(f"🔧 Tool result: {result}")
                
                # Add tool results to the response
                if tool_results:
                    response.content += f"\n\nTool Results:\n" + "\n".join(tool_results)
            else:
                print("🔧 No tool calls detected in response")
        else:
            response = self.llm.invoke(llm_messages)
        
        # Ensure response is always a string
        if isinstance(response.content, list):
            return '\n'.join(str(item) for item in response.content)
        return str(response.content)

# Global agent instance
learner_agent = LearnerAgent()
