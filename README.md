# Browser Python with Thebe + JupyterLite

A minimal, static web app that runs Python entirely **in the browser** using Thebe + JupyterLite (Pyodide). No backend server required!

## What This Is

This single-page application provides a notebook-like interface where you can:
- Write and execute Python code directly in your browser
- Dynamically add new executable code cells
- Install pure-Python packages using `micropip`
- Download your work as a Jupyter notebook (.ipynb)

## Technology Stack

- **Thebe**: Provides the executable code cell interface
- **JupyterLite**: Browser-based Jupyter environment
- **Pyodide**: Python interpreter compiled to WebAssembly
- **Static HTML/CSS/JS**: No server-side dependencies

## Features

- ➕ **Add Code Cell**: Create new executable Python cells on demand
- 📦 **Add micropip Demo**: Insert a cell showing how to install packages like `pydantic`
- ▶️ **Run All**: Execute all cells in sequence
- 🗑️ **Delete Last Cell**: Remove the most recently added cell
- 💾 **Download .ipynb**: Export your work as a Jupyter notebook

## Limitations

⚠️ **Important**: This runs Python in the browser using Pyodide, which has some limitations:

- **Heavy/Native Libraries**: Libraries requiring C extensions, GPU acceleration, or system-level access won't work
- **Package Availability**: Only pure-Python packages or those specifically compiled for Pyodide are available
- **First Load**: Initial startup takes time while Pyodide downloads (~10-30 seconds)
- **Memory**: Limited to browser memory constraints

### What Works Well
- Pure Python code (NumPy, SciPy, Matplotlib, Pandas, etc.)
- Data analysis and visualization
- Web APIs and HTTP requests
- Many scientific computing packages

### What Doesn't Work
- TensorFlow, PyTorch (native versions)
- OpenCV (use opencv-python-headless if available)
- Packages requiring system libraries
- File system operations outside the browser sandbox

## Running Locally

### Option 1: Python Built-in Server
```bash
# Navigate to the project directory
cd /path/to/this/project

# Start a local server
python3 -m http.server 8000

# Open in browser
# Go to: http://localhost:8000
```

### Option 2: Node.js (if you have package.json set up)
```bash
# Install dependencies (only needed once)
npm install

# Start development server
npm run dev

# Open in browser
# Go to: http://localhost:8000
```

### Option 3: Any Static Server
You can use any static file server:
- `serve` (npm package)
- Live Server (VS Code extension)
- Local Apache/Nginx
- Python's `http.server`

## First-Time Usage

1. Open `index.html` in your browser via a local server (required for security)
2. Wait for "Kernel connected and ready!" status message
3. Click the run button (▶️) on the pre-loaded cell to test NumPy
4. Try adding new cells and running them

## Package Installation Example

The "Add micropip Demo" button shows how to install packages:

```python
import micropip
await micropip.install("pydantic==2.9.0")
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

User(id=1, name="Ada")
```

## Vendoring Assets (Optional)

If you need to work offline or have strict CSP policies, you can vendor the Thebe assets:

1. Create a `thebe/` directory in your project
2. Download the required files:
   - `https://unpkg.com/thebe@0.8.2/lib/index.css`
   - `https://unpkg.com/thebe@0.8.2/lib/index.js`
   - `https://unpkg.com/@jupyterlite/pyodide-kernel-extension@0.0.6/lib/index.js`
3. Update the script/link tags in `index.html` to point to local files

Or use the provided script:
```bash
./scripts/fetch-thebe-assets.sh
```

## Troubleshooting

### Common Issues

1. **"Failed to load kernel"**
   - Make sure you're serving via HTTP/HTTPS, not opening file:// directly
   - Check browser console for specific error messages

2. **Long loading times**
   - First load downloads Pyodide (~50MB), subsequent loads are faster
   - Consider showing a loading spinner for better UX

3. **Package not found with micropip**
   - Check [Pyodide packages list](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)
   - Try installing with specific version: `micropip.install("package==version")`

4. **CSP (Content Security Policy) errors**
   - If using strict CSP, vendor the assets locally
   - Allow `unsafe-eval` for Pyodide (or use appropriate CSP for WASM)

### Browser Compatibility

- **Recommended**: Chrome, Firefox, Safari (latest versions)
- **Required**: WebAssembly support
- **Note**: Some older browsers may not support all features

## Development

This is a single-file static app, but you can extend it by:

- Adding more UI controls for notebook management
- Implementing cell reordering (drag & drop)
- Adding syntax highlighting
- Persistent storage (localStorage or IndexedDB)
- Integration with GitHub/GitLab for saving notebooks

## License

MIT License - feel free to use and modify as needed.
