# Livestream App Monorepo

This repository contains a complete RTSP livestreaming application with overlay management:

- `backend` – FastAPI service providing RTSP→HLS conversion and overlay CRUD operations
- `frontend` – Next.js application for viewing streams and managing overlays

## Features

- **RTSP to HLS Streaming**: Convert RTSP streams to web-compatible HLS format
- **Real-time Overlay Management**: Add, position, and manage text overlays on video streams
- **Drag & Drop Interface**: Intuitive overlay positioning with live preview
- **RESTful API**: Complete CRUD operations for overlays and stream management
- **Cross-platform**: Works on Windows, macOS, and Linux

## Prerequisites

### Required Software

1. **Python 3.10+** - For the backend service
2. **Node.js 18+** - For the frontend application
3. **FFmpeg** - For video stream processing (see setup below)

### FFmpeg Installation

FFmpeg is required for RTSP to HLS conversion.

#### Windows:

1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables" → Edit "Path" → Add new entry
4. Verify: Open new Command Prompt and run `ffmpeg -version`

#### macOS:

```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install ffmpeg
```

## Getting Started

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will be available at [http://localhost:8000](http://localhost:8000)

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### 3. Using the Application

1. Open [http://localhost:3000](http://localhost:3000) in your browser
2. Enter an RTSP URL (e.g., `rtsp://example.com/stream`)
3. Click "Load Stream" to start conversion
4. Once the video loads, use the overlay management panel to:
   - Add text overlays
   - Drag overlays to position them
   - Delete overlays as needed

## API Documentation

Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs)

### Key Endpoints

- `POST /api/streams/start` - Start RTSP→HLS conversion
- `POST /api/streams/stop/{stream_id}` - Stop stream conversion
- `GET /api/streams/active` - List active streams
- `GET /api/overlays` - List all overlays
- `POST /api/overlays` - Create new overlay
- `PUT /api/overlays/{id}` - Update overlay
- `DELETE /api/overlays/{id}` - Delete overlay

## Optional: MongoDB Setup

By default, the application uses in-memory storage. For persistent data:

1. Install MongoDB or use Docker:

   ```bash
   docker run -d -p 27017:27017 mongo:7
   ```

2. Set environment variables:
   ```bash
   # In backend/.env
   USE_MONGO=1
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=livestream
   ```

## Docker Deployment

For containerized deployment:

```bash
docker-compose up -d
```

This starts all services including MongoDB.

## Troubleshooting

### Common Issues

**"FFmpeg not found"**: Ensure FFmpeg is installed and in your system PATH. Restart your terminal after installation.

**Stream won't load**: Verify the RTSP URL works in a media player like VLC. Some streams require authentication or specific network configurations.

**Overlay positioning**: Overlays are positioned relative to the video player. Ensure the video has loaded before adding overlays.

## Development Roadmap

- [x] Backend overlay CRUD operations
- [x] RTSP ingest & HLS output pipeline
- [x] Frontend Next.js application
- [x] Overlay UI with drag & drop
- [ ] Server-side overlay rendering with FFmpeg
- [ ] Image overlay support
- [ ] Multiple stream management
- [ ] User authentication
- [ ] Stream recording capabilities
