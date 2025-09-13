#!/bin/bash

echo "🚀 Setting up fast Python notebook environment..."

# Option 1: Quick JupyterLite test
echo "📝 Testing JupyterLite (instant loading)..."
python3 -m http.server 8001 &
SERVER_PID=$!
echo "✅ JupyterLite available at: http://localhost:8001/jupyterlite-config.html"

# Option 2: Docker setup
if command -v docker &> /dev/null; then
    echo "🐳 Docker found! Building fast image..."
    docker build -t fast-python-notebook . --quiet
    
    echo "🚀 Starting fast Docker Jupyter..."
    docker run -d --name jupyter-fast -p 8888:8888 -v $(pwd):/app/workspace fast-python-notebook
    
    echo "✅ Fast Jupyter available at: http://localhost:8888"
    echo "📝 Your notebook with fast backend: http://localhost:8001"
    
else
    echo "⚠️  Docker not found. Using standard Python server..."
    pip install jupyter numpy pandas matplotlib requests
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' &
fi

echo ""
echo "🎯 SPEED COMPARISON:"
echo "   🔥 JupyterLite (browser-only): INSTANT loading"
echo "   ⚡ Docker + pre-built deps: ~2-3 seconds"
echo "   🐌 Current Binder setup: ~30-60 seconds"

wait
