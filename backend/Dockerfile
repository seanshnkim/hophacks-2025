# Use official Python image
FROM python:3.10-slim

# Install system dependencies for Manim and ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt ./
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Set environment variables (optional, for .env support)
ENV PYTHONUNBUFFERED=1

# Run the FastAPI app
CMD ["python", "run.py"]