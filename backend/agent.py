from typing import List, Dict, Any
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from configs import config

class LearnerAgent:
    """Simple learning agent using Gemini Flash 2.5"""
    
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
    
    def get_response(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Get a response from the agent given a system prompt and message history"""
        
        # Prepare messages for the LLM
        llm_messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in messages:
            if msg["role"] == "user":
                llm_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                llm_messages.append(AIMessage(content=msg["content"]))
        
        # Get response from LLM
        response = self.llm.invoke(llm_messages)
        
        return response.content

# Global agent instance
learner_agent = LearnerAgent()
