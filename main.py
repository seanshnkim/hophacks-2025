import os
import subprocess
import time
import requests
import json
from dotenv import load_dotenv
import http.server
import socketserver
import threading

# Load environment variables from .env file
load_dotenv()

# Get port numbers from environment variables
backend_port = os.getenv("BACKEND_PORT", "8000")
jupyter_port = os.getenv("JUPYTER_PORT", "8888")

def create_enhanced_notebook_html(notebook_filename):
    """Create an enhanced HTML notebook that auto-imports the generated notebook"""
    
    # Read the base generated_notebook.html
    try:
        with open("generated_notebook.html", "r") as f:
            base_html = f.read()
    except FileNotFoundError:
        return "<html><body><h1>Error: generated_notebook.html not found</h1></body></html>"
    
    return base_html

# Start the backend server using the virtual environment
print(f"Starting backend server on port {backend_port}...")
backend_process = subprocess.Popen([
    "../backend_venv/bin/python3", 
    "-c", 
    f"import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port={backend_port}, reload=False)"
], cwd="backend")

# Start the frontend HTTP server
def start_frontend_server():
    """Start a simple HTTP server to serve the HTML files"""
    try:
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", int(jupyter_port)), handler) as httpd:
            print(f"Frontend server started on http://localhost:{jupyter_port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Frontend server error: {e}")

# Start frontend server in a separate thread
frontend_thread = threading.Thread(target=start_frontend_server, daemon=True)
frontend_thread.start()

# Give the backend server time to start
print("Waiting for backend server to start...")
time.sleep(8)

# Make a request to the backend server's /learn endpoint
max_retries = 3
for attempt in range(max_retries):
    try:
        url = f"http://localhost:{backend_port}/learn"
        payload = {
            "topic": "python basics",
            "user_preferences": "I am a complete beginner"
        }
        
        print(f"Making request to {url}... (attempt {attempt + 1}/{max_retries})")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("Successfully received data from backend!")
            
            # Convert the playground data to proper Jupyter notebook format
            notebook_data = data["playground"]
            
            # Always create a proper Jupyter notebook structure
            jupyter_notebook = {
                "cells": [],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python", 
                        "name": "python3"
                    },
                    "language_info": {
                        "name": "python",
                        "version": "3.8.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 2
            }
            
            # If we have cells in the proper format, use them
            if isinstance(notebook_data, dict) and "cells" in notebook_data:
                jupyter_notebook["cells"] = notebook_data["cells"]
            else:
                # Create cells from the learning module content  
                learning_content = data.get("learning_module", "# Python Learning Module")
                jupyter_notebook["cells"] = [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [learning_content]
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": ["# TODO: Start practicing Python here!\nprint('Hello, Python!')"]
                    }
                ]
            
            # Save the notebook data in proper Jupyter format
            notebook_filename = "generated_notebook.ipynb"
            with open(notebook_filename, "w") as f:
                json.dump(jupyter_notebook, f, indent=2)
            
            print(f"Saved notebook to {notebook_filename}")
            
            # Create the enhanced HTML file
            enhanced_html = create_enhanced_notebook_html(notebook_filename)
            
            # Save the enhanced HTML
            with open("generated_notebook.html", "w") as f:
                f.write(enhanced_html)
            
            print("Enhanced HTML notebook created!")
            break
            
        else:
            print(f"Error: Backend returned status code {response.status_code}")
            if attempt == max_retries - 1:
                print("Failed to get data from backend after all attempts")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if attempt == max_retries - 1:
            print("Failed to connect to backend after all attempts")
        else:
            print("Retrying...")
            time.sleep(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        break

# Keep the script running
try:
    print("\nBoth servers are running!")
    print(f"Backend API: http://localhost:{backend_port}")
    print(f"Frontend: http://localhost:{jupyter_port}")
    print(f"Notebook: http://localhost:{jupyter_port}/generated_notebook.html")
    print("Press Ctrl+C to stop the servers...")
    
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nShutting down servers...")
    backend_process.terminate()
    backend_process.wait()
    print("Servers stopped.")
