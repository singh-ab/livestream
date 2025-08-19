# How to Use the RTSP Livestream App

This application allows you to view RTSP streams and add overlays to them.

## Prerequisites

- Node.js and npm for the frontend
- Python 3.10+ for the backend
- FFmpeg installed and available in your system's PATH
- MongoDB (optional, currently uses in-memory database by default)

## Starting the Application

### Backend (FastAPI)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment (if not already created):

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the backend server:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000

### Frontend (Next.js)

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

   The frontend will be available at http://localhost:3000

## Using the Application

1. Open the frontend in your browser (http://localhost:3000)
2. Enter an RTSP URL in the input field (e.g., a test RTSP stream)
3. Click "Load Stream" to start the RTSP to HLS conversion
4. Once the stream starts playing, you can add and manage overlays:
   - Enter text in the "Enter overlay text" input field
   - Click "Add Overlay" to create a new text overlay
   - Drag the overlay to position it on the video
   - Use the list below to manage (delete) existing overlays

## API Documentation

Access the API documentation at http://localhost:8000/docs

### Key Endpoints

- `POST /api/streams/start` - Start a new stream conversion
- `POST /api/streams/stop/{stream_id}` - Stop a running stream
- `GET /api/streams/active` - List active streams
- `GET /api/overlays` - List all overlays
- `POST /api/overlays` - Create a new overlay
- `PUT /api/overlays/{overlay_id}` - Update an overlay
- `DELETE /api/overlays/{overlay_id}` - Delete an overlay

## Notes

- RTSP streams may take a few seconds to load and convert to HLS
- For production use, consider configuring a proper MongoDB connection
- All overlays are currently "text" type. Image overlays will be supported in future versions
