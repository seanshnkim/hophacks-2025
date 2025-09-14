import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for environment variables"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # LLM Configuration
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    
    # App Configuration
    APP_NAME = os.getenv("APP_NAME", "HopHacks 2025 Learner App")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Validate numeric ranges
        if not (0.0 <= cls.LLM_TEMPERATURE <= 2.0):
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0")
        
        if cls.LLM_MAX_TOKENS <= 0:
            raise ValueError("LLM_MAX_TOKENS must be a positive integer")
        
        return True

# Create a global config instance
config = Config()

# Validate configuration on import
config.validate_config()
