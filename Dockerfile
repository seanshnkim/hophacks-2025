# Multi-stage Docker build for fast Python notebook
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages upfront
RUN pip install --no-cache-dir \
    jupyter \
    numpy \
    pandas \
    matplotlib \
    requests \
    scipy \
    scikit-learn \
    plotly

# Production stage
FROM base as production

WORKDIR /app
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter with custom config
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
