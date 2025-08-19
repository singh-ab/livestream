# Livestream App Monorepo

This repository contains:

- `backend` – FastAPI service providing overlay CRUD and (planned) RTSP->HLS handling.
- `frontend` – Next.js application for viewing the stream and managing overlays (to be added).

## Getting Started (Planned)

Backend quick start and frontend setup instructions will be added as implementation progresses.

### Dev (anticipated)

1. Install backend deps: `pip install -r requirements.txt`
2. Run backend: `uvicorn app.main:app --reload`
3. Install frontend deps: `npm install` inside `frontend`
4. Run frontend: `npm run dev`
5. Open [http://localhost:3000]

## Roadmap

1. Backend overlay CRUD (in-memory -> MongoDB)
2. RTSP ingest & HLS output pipeline
3. Frontend Next.js scaffold
4. Overlay UI (drag, resize, save)
5. Integrate overlays into live video (client-side first, then server-side FFmpeg)
6. Documentation & deployment configs
