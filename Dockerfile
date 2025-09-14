# Multi-stage Docker build for HopHacks 2025 Backend API
FROM python:3.11-slim AS base

# Install system dependencies required for Manim and other libraries
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    # System libraries
    curl \
    wget \
    git \
    # LaTeX for Manim (minimal installation)
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    # FFmpeg for video processing
    ffmpeg \
    # Image processing libraries
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    # Additional dependencies for Manim
    libgl1-mesa-dri \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MANIM_QUALITY=medium_quality
ENV MANIM_VERBOSE=INFO

# Default values for API keys (should be overridden at runtime)
ENV GEMINI_API_KEY=""
ENV GEMINI_MODEL=gemini-2.0-flash-exp
ENV LLM_TEMPERATURE=0.7
ENV LLM_MAX_TOKENS=8192

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional dependencies that might be needed
RUN pip install --no-cache-dir \
    # Additional visualization libraries
    matplotlib \
    seaborn \
    plotly \
    # Jupyter notebook support
    jupyter \
    ipykernel \
    # Additional utilities
    python-multipart \
    aiofiles

# Copy backend code
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p visualizations notebooks

# Set working directory to backend
WORKDIR /app/backend

# Expose the FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI application
CMD ["python", "main.py"]