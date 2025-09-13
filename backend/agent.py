from typing import List, Dict, Any, TypedDict
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from configs import config
from datetime import datetime

class AgentState(TypedDict):
    """State for the LangGraph agent"""
    topic: str
    user_preferences: str
    response: str
    user_message: str

class LearnerAgent:
    """LangGraph-based learning agent using Gemini Flash 2.5"""
    
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
        
        # Message history
        self.messages: List[Dict[str, str]] = []
        
        # Initialize the graph
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        def process_learning_request(state: AgentState) -> AgentState:
            """Process the learning request and generate response"""
            topic = state.get("topic", "")
            user_preferences = state.get("user_preferences", "")
            
            # Create system message for learning context
            system_prompt = self._create_system_prompt(user_preferences)
            
            # Prepare messages for the LLM
            llm_messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history
            for msg in self.messages:
                if msg["role"] == "user":
                    llm_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    llm_messages.append(AIMessage(content=msg["content"]))
            
            # Add current user message
            user_message = f"I want to learn about: {topic}"
            llm_messages.append(HumanMessage(content=user_message))
            
            # Get response from LLM
            response = self.llm.invoke(llm_messages)
            
            # Update state with response
            return {
                "topic": topic,
                "user_preferences": user_preferences,
                "response": response.content,
                "user_message": user_message
            }
        
        # Create the graph
        workflow = StateGraph(AgentState)
        workflow.add_node("process_request", process_learning_request)
        workflow.set_entry_point("process_request")
        workflow.add_edge("process_request", END)
        
        return workflow.compile()
    
    def _create_system_prompt(self, user_preferences: str) -> str:
        """Create system prompt based on user preferences"""
        
        base_prompt = """You are an expert learning assistant designed to help users understand complex topics.

Guidelines:
- Provide clear, educational explanations tailored to the user's needs
- Break down complex topics into understandable parts
- Use examples and analogies when helpful
- Be encouraging and supportive
- Adapt your teaching style based on the user's preferences

Always be encouraging, clear, and educational."""
        
        if user_preferences and user_preferences.strip():
            return f"""{base_prompt}

User Preferences: {user_preferences}

Please tailor your response to match these preferences as much as possible."""
        else:
            return base_prompt
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_response(self, topic: str, user_preferences: str) -> str:
        """Get a response from the agent for a learning topic"""
        
        # Prepare initial state
        initial_state = {
            "topic": topic,
            "user_preferences": user_preferences
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Extract response
        response = result.get("response", "I'm sorry, I couldn't generate a response.")
        user_message = result.get("user_message", "")
        
        # Add messages to history
        self.add_message("user", user_message)
        self.add_message("assistant", response)
        
        return response
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.messages.copy()

# Global agent instance
learner_agent = LearnerAgent()
