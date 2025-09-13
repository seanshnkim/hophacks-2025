#!/usr/bin/env python3
"""
Development server runner for the FastAPI application.
Run this file to start the development server.
"""

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
