# Backend - Learning API

AI-powered learning assistant API that generates educational content and interactive Jupyter notebooks.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env` (if available)
   - Add your Gemini API key to `.env`:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Running the Server

**Start the development server:**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /learn` - Generate learning content and playground notebook
- `GET /health` - Health check

## Testing

Run the test script to generate a sample notebook:
```bash
python test_endpoint.py
```

This will create a `playground_YYYYMMDD_HHMMSS.ipynb` file that you can open in Jupyter.
