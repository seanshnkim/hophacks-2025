import os
import subprocess
import time
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get port numbers from environment variables
backend_port = os.getenv("BACKEND_PORT")
jupyter_port = os.getenv("JUPYTER_PORT")

if not backend_port or not jupyter_port:
    print("Error: Port numbers not found in .env file")
    exit(1)

# Start the backend server using the virtual environment
print(f"Starting backend server on port {backend_port}...")
backend_process = subprocess.Popen([
    "../backend_venv/bin/python3", 
    "-c", 
    f"import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port={backend_port}, reload=False)"
], cwd="backend")

# Give the backend server time to start
print("Waiting for backend server to start...")
time.sleep(8)  # Increased wait time

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
            break
        else:
            print(f"Error: Backend returned status code {response.status_code}")
            if attempt == max_retries - 1:
                raise Exception(f"Backend returned status code {response.status_code}")
            
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print(f"Error making request to backend server after {max_retries} attempts: {e}")
            data = None
            break

# Process the data if we got a successful response
if data:
    # Extract the playground part
    if "playground" in data:
        playground_data = data["playground"]
        
        # Ensure proper notebook structure
        if "cells" not in playground_data:
            playground_data["cells"] = []
        if "metadata" not in playground_data:
            playground_data["metadata"] = {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11+"
                }
            }
        if "nbformat" not in playground_data:
            playground_data["nbformat"] = 4
        if "nbformat_minor" not in playground_data:
            playground_data["nbformat_minor"] = 4
        
        # Save the playground data as a proper .ipynb file
        notebook_filename = "generated_notebook.ipynb"
        with open(notebook_filename, "w") as f:
            json.dump(playground_data, f, indent=2)
        
        print(f"✅ Generated notebook saved as {notebook_filename}")
        
        # Also save raw data for reference
        with open("notebook_data.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Create simple enhanced HTML (just copy with new title)
        try:
            with open("index.html", "r") as f:
                base_html = f.read()
            enhanced_html = base_html.replace(
                '<title>🚀 Fast Python Browser Notebook - No Servers!</title>',
                '<title>🤖 AI-Generated Learning Notebook - Manual Import</title>'
            ).replace(
                '<p class="subtitle">⚡ Powered by Pyodide - Loads in 3 seconds, runs entirely in your browser</p>',
                '<p class="subtitle">🤖 AI-Generated Content Ready! Use "📁 Import .ipynb" to load generated_notebook.ipynb</p>'
            )
            
            with open("generated_notebook.html", "w") as f:
                f.write(enhanced_html)
        except Exception as e:
            print(f"Warning: Could not create enhanced HTML: {e}")
        
        print(f"🚀 Enhanced notebook interface created!")
        print(f"📄 Raw response saved to notebook_data.json")
        
    else:
        print("Error: No playground data found in response")
else:
    print("⚠️  No data received from backend. Creating basic notebook interface...")
    # Create basic notebook interface without auto-import
    try:
        with open("index.html", "r") as f:
            basic_html = f.read()
        with open("generated_notebook.html", "w") as f:
            f.write(basic_html.replace(
                '<title>🚀 Fast Python Browser Notebook - No Servers!</title>',
                '<title>🚀 Fast Python Browser Notebook - Manual Mode</title>'
            ))
        print("📝 Basic notebook interface created as fallback")
    except:
        print("❌ Could not create fallback interface")

# Start the Jupyter server (HTTP server)
print(f"\n🚀 Starting HTTP server on port {jupyter_port}...")
jupyter_process = subprocess.Popen(["python3", "-m", "http.server", jupyter_port])

# Give the HTTP server time to start
time.sleep(2)

# Keep the processes running until interrupted
try:
    print("\n" + "="*60)
    print("🎉 SERVERS ARE RUNNING!")
    print("="*60)
    print(f"🤖 AI-Generated Notebook: http://localhost:{jupyter_port}/generated_notebook.html")
    print(f"📄 Original Notebook UI:  http://localhost:{jupyter_port}/index.html")
    print(f"⚙️  Backend API:           http://localhost:{backend_port}")
    print(f"📊 Raw Notebook Data:     http://localhost:{jupyter_port}/generated_notebook.ipynb")
    print("="*60)
    print("💡 Visit the AI-Generated Notebook and use '📁 Import .ipynb' to load the generated content!")
    print("💡 Press Ctrl+C to stop all servers")
    print("="*60)
    
    backend_process.wait()
    jupyter_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping servers...")
    backend_process.terminate()
    jupyter_process.terminate()
    print("✅ All servers stopped!")
