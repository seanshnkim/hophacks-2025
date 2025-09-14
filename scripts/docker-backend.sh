#!/bin/bash

# Docker Backend Management Script for HopHacks 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="hophacks-backend"
CONTAINER_NAME="hophacks-backend-container"
PORT="8000"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the Docker container"
    echo "  stop      Stop the running container"
    echo "  restart   Restart the container"
    echo "  logs      Show container logs"
    echo "  shell     Open shell in running container"
    echo "  clean     Remove container and image"
    echo "  help      Show this help message"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT    Port to expose (default: 8000)"
    echo "  -n, --name NAME    Container name (default: hophacks-backend-container)"
    echo "  -i, --image NAME   Image name (default: hophacks-backend)"
    echo ""
    echo "Environment Variables (Required for 'run' command):"
    echo "  GEMINI_API_KEY     Your Google Gemini API key (required)"
    echo "  GEMINI_MODEL       Gemini model to use (default: gemini-2.0-flash-exp)"
    echo "  LLM_TEMPERATURE    LLM temperature (default: 0.7)"
    echo "  LLM_MAX_TOKENS     Max tokens (default: 8192)"
    echo "  MANIM_QUALITY      Manim quality (default: medium_quality)"
    echo "  MANIM_VERBOSE      Manim verbosity (default: INFO)"
    echo ""
    echo "Examples:"
    echo "  # Set API key and build"
    echo "  export GEMINI_API_KEY='your_key_here'"
    echo "  $0 build"
    echo "  $0 run"
    echo ""
    echo "  # Or set inline"
    echo "  GEMINI_API_KEY='your_key' $0 run"
    echo ""
    echo "  # Other commands"
    echo "  $0 logs"
    echo "  $0 clean"
}

# Function to build the image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME"
    
    if docker build -t "$IMAGE_NAME" .; then
        print_success "Image built successfully: $IMAGE_NAME"
    else
        print_error "Failed to build image"
        exit 1
    fi
}

# Function to run the container
run_container() {
    print_status "Starting container: $CONTAINER_NAME"
    
    # Check for required environment variables
    if [ -z "$GEMINI_API_KEY" ]; then
        print_error "GEMINI_API_KEY environment variable is required!"
        print_status "Set it with: export GEMINI_API_KEY='your_api_key_here'"
        print_status "Or run: GEMINI_API_KEY='your_key' $0 run"
        exit 1
    fi
    
    # Check if container already exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        print_warning "Container $CONTAINER_NAME already exists. Stopping and removing it first."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
    fi
    
    # Prepare environment variables
    ENV_ARGS=""
    if [ -n "$GEMINI_API_KEY" ]; then
        ENV_ARGS="$ENV_ARGS -e GEMINI_API_KEY=$GEMINI_API_KEY"
    fi
    if [ -n "$GEMINI_MODEL" ]; then
        ENV_ARGS="$ENV_ARGS -e GEMINI_MODEL=$GEMINI_MODEL"
    fi
    if [ -n "$LLM_TEMPERATURE" ]; then
        ENV_ARGS="$ENV_ARGS -e LLM_TEMPERATURE=$LLM_TEMPERATURE"
    fi
    if [ -n "$LLM_MAX_TOKENS" ]; then
        ENV_ARGS="$ENV_ARGS -e LLM_MAX_TOKENS=$LLM_MAX_TOKENS"
    fi
    if [ -n "$MANIM_QUALITY" ]; then
        ENV_ARGS="$ENV_ARGS -e MANIM_QUALITY=$MANIM_QUALITY"
    fi
    if [ -n "$MANIM_VERBOSE" ]; then
        ENV_ARGS="$ENV_ARGS -e MANIM_VERBOSE=$MANIM_VERBOSE"
    fi
    
    # Run the container
    if docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:8000" \
        -v "$(pwd)/backend/visualizations:/app/backend/visualizations" \
        -v "$(pwd)/backend/notebooks:/app/backend/notebooks" \
        $ENV_ARGS \
        "$IMAGE_NAME"; then
        print_success "Container started successfully!"
        print_status "Backend API available at: http://localhost:$PORT"
        print_status "Health check: http://localhost:$PORT/health"
        print_status "API docs: http://localhost:$PORT/docs"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to stop the container
stop_container() {
    print_status "Stopping container: $CONTAINER_NAME"
    
    if docker stop "$CONTAINER_NAME" 2>/dev/null; then
        print_success "Container stopped successfully"
    else
        print_warning "Container $CONTAINER_NAME is not running or doesn't exist"
    fi
}

# Function to restart the container
restart_container() {
    print_status "Restarting container: $CONTAINER_NAME"
    stop_container
    run_container
}

# Function to show logs
show_logs() {
    print_status "Showing logs for container: $CONTAINER_NAME"
    
    if docker ps --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        docker logs -f "$CONTAINER_NAME"
    else
        print_error "Container $CONTAINER_NAME is not running"
        exit 1
    fi
}

# Function to open shell in container
open_shell() {
    print_status "Opening shell in container: $CONTAINER_NAME"
    
    if docker ps --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        docker exec -it "$CONTAINER_NAME" /bin/bash
    else
        print_error "Container $CONTAINER_NAME is not running"
        exit 1
    fi
}

# Function to clean up
clean_up() {
    print_status "Cleaning up container and image"
    
    # Stop and remove container
    if docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        print_success "Container removed"
    fi
    
    # Remove image
    if docker images --format "table {{.Repository}}" | grep -q "^$IMAGE_NAME$"; then
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
        print_success "Image removed"
    fi
}

# Parse command line arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        build|run|stop|restart|logs|shell|clean|help)
            COMMAND="$1"
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_up
        ;;
    help|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac
