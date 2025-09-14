#!/bin/bash

# Script to download and vendor Thebe assets locally
# This is useful for offline usage or strict CSP policies

set -e

# Create thebe directory if it doesn't exist
mkdir -p thebe

echo "📥 Downloading Thebe assets..."

# Download Thebe CSS
echo "Downloading Thebe CSS..."
curl -L -o thebe/thebe.css "https://unpkg.com/thebe@0.8.2/lib/index.css"

# Download Thebe JS
echo "Downloading Thebe JS..."
curl -L -o thebe/thebe.js "https://unpkg.com/thebe@0.8.2/lib/index.js"

# Download JupyterLite Pyodide kernel extension
echo "Downloading JupyterLite Pyodide kernel..."
curl -L -o thebe/jupyterlite-pyodide-kernel.js "https://unpkg.com/@jupyterlite/pyodide-kernel-extension@0.0.6/lib/index.js"

echo "✅ Assets downloaded to ./thebe/ directory"
echo ""
echo "To use local assets, update index.html:"
echo "  - Change CSS link to: ./thebe/thebe.css"
echo "  - Change Thebe script to: ./thebe/thebe.js"
echo "  - Change JupyterLite script to: ./thebe/jupyterlite-pyodide-kernel.js"
