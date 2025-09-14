# AI Learning Module Frontend

A modern React frontend for the AI-powered learning module generator.

## Features

- **Topic Selection**: Choose from suggested topics or enter your own
- **Personalization**: Select learning preferences and styles
- **Interactive Learning**: View learning blocks with rich content
- **Video Visualizations**: Play educational videos with custom controls
- **Real-time Data**: View API responses and debugging information
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Backend server running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Select a Topic**: Choose from suggested topics or enter your own
2. **Customize Learning**: Select preferences like "I want visual examples" or "I am a beginner"
3. **Generate Module**: Click "Generate Learning Module" to create your personalized learning experience
4. **Learn**: Browse through learning blocks, read content, and watch visualizations
5. **Debug**: View the JSON response data on the right side for development

## Components

- **TopicForm**: Topic selection and personalization form
- **LearningModule**: Displays learning blocks with content and videos
- **VideoPlayer**: Custom video player with play/pause controls
- **JsonDisplay**: Shows API response data for debugging

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- `POST /learn` - Generate learning modules
- `GET /visualization/{path}` - Serve video files
- `GET /health` - Check API health

## Technologies

- React 18 with TypeScript
- Material-UI for components and styling
- Axios for API communication
- Context API for state management