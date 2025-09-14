# Docker Setup for HopHacks 2025 Backend

This document explains how to build and run the backend API using Docker, including all dependencies for Manim visualizations.

## Prerequisites

- Docker installed on your system
- At least 4GB of available RAM
- At least 2GB of free disk space

## Quick Start

### Using the Management Script

The easiest way to manage the Docker container is using the provided script:

```bash
# Build the Docker image
./scripts/docker-backend.sh build

# Run the container
./scripts/docker-backend.sh run

# View logs
./scripts/docker-backend.sh logs

# Stop the container
./scripts/docker-backend.sh stop

# Clean up (remove container and image)
./scripts/docker-backend.sh clean
```

### Manual Docker Commands

If you prefer to use Docker commands directly:

```bash
# Build the image
docker build -t hophacks-backend .

# Run the container
docker run -d \
  --name hophacks-backend-container \
  -p 8000:8000 \
  -v $(pwd)/backend/visualizations:/app/backend/visualizations \
  -v $(pwd)/backend/notebooks:/app/backend/notebooks \
  hophacks-backend

# View logs
docker logs -f hophacks-backend-container

# Stop the container
docker stop hophacks-backend-container

# Remove the container
docker rm hophacks-backend-container
```

## What's Included

The Docker image includes:

### System Dependencies
- **Python 3.11** - Base runtime
- **LaTeX** - Required for Manim mathematical rendering
- **FFmpeg** - Video processing for Manim animations
- **Cairo/Pango** - Graphics libraries for Manim
- **OpenGL** - Hardware acceleration support

### Python Dependencies
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Manim** - Mathematical animation engine
- **LangChain** - LLM integration
- **Google Generative AI** - Gemini API client
- **Pydantic** - Data validation
- **Jupyter** - Notebook support

## Environment Variables

The container expects these environment variables (set them in your environment or `.env` file):

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (with defaults)
GEMINI_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192
MANIM_QUALITY=medium_quality
MANIM_VERBOSE=INFO
```

## API Endpoints

Once running, the API will be available at `http://localhost:8000`:

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **Learning Endpoint**: `POST /learn`
- **Visualizations**: `GET /visualization/{filename}`
- **Notebooks**: `GET /notebook/{filename}`

## Volumes

The container mounts two volumes for persistent storage:

- `./backend/visualizations` → `/app/backend/visualizations` - Stores generated MP4 videos
- `./backend/notebooks` → `/app/backend/notebooks` - Stores generated Jupyter notebooks

## Troubleshooting

### Common Issues

1. **Out of Memory**: Manim requires significant RAM. Ensure you have at least 4GB available.

2. **LaTeX Errors**: If you see LaTeX-related errors, the container includes a minimal LaTeX installation. For complex mathematical expressions, you might need additional LaTeX packages.

3. **FFmpeg Issues**: Video generation requires FFmpeg. The container includes FFmpeg, but if you encounter issues, check the logs.

4. **API Key Missing**: Make sure to set the `GEMINI_API_KEY` environment variable.

### Debugging

```bash
# Open a shell in the running container
./scripts/docker-backend.sh shell

# Or manually
docker exec -it hophacks-backend-container /bin/bash

# Check container logs
docker logs hophacks-backend-container

# Check container status
docker ps -a
```

### Performance Optimization

For better performance:

1. **Increase Memory**: Allocate more RAM to Docker
2. **Use SSD**: Store volumes on SSD for faster I/O
3. **Quality Settings**: Adjust `MANIM_QUALITY` environment variable:
   - `low_quality` - Fastest, lowest quality
   - `medium_quality` - Balanced (default)
   - `high_quality` - Best quality, slower

## Development

For development, you can mount the entire backend directory:

```bash
docker run -d \
  --name hophacks-backend-dev \
  -p 8000:8000 \
  -v $(pwd)/backend:/app/backend \
  hophacks-backend
```

This allows you to edit code and see changes without rebuilding the image.

## Production Considerations

For production deployment:

1. **Security**: Change the default CORS settings in `main.py`
2. **Environment Variables**: Use proper secret management
3. **Resource Limits**: Set appropriate CPU and memory limits
4. **Health Checks**: The container includes health checks
5. **Logging**: Configure proper logging levels
6. **Monitoring**: Add monitoring and alerting

## File Structure

```
/app/
├── backend/                 # Backend code
│   ├── main.py            # FastAPI application
│   ├── agent.py           # LLM agent
│   ├── learning_blocks.py # Learning block processor
│   ├── tools.py           # Visualization tools
│   ├── configs.py         # Configuration
│   ├── prompts.py         # LLM prompts
│   ├── visualizations/    # Generated videos (mounted)
│   └── notebooks/         # Generated notebooks (mounted)
└── requirements.txt       # Python dependencies
```

## Support

If you encounter issues:

1. Check the container logs: `docker logs hophacks-backend-container`
2. Verify environment variables are set correctly
3. Ensure sufficient system resources (RAM, disk space)
4. Check that all required ports are available

For additional help, refer to the main project README or create an issue in the repository.
