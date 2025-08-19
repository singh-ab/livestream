from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import overlays, docs, stream
from .stream_manager import STREAMS_BASE_DIR
from .ffmpeg_finder import find_ffmpeg_installations, is_ffmpeg_working
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create streams directory if it doesn't exist
os.makedirs(STREAMS_BASE_DIR, exist_ok=True)

# Check FFmpeg availability at startup
ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
if not is_ffmpeg_working(ffmpeg_path):
    logger.warning(f"FFmpeg not working at configured path: {ffmpeg_path}")
    installations = find_ffmpeg_installations()
    if installations:
        working_paths = [p for p in installations if is_ffmpeg_working(p)]
        if working_paths:
            logger.info(f"Found working FFmpeg at: {working_paths[0]}")
            logger.info(f"Set FFMPEG_PATH environment variable to use this installation")
        else:
            logger.warning(f"Found FFmpeg installations but none are working: {installations}")
    else:
        logger.warning("No FFmpeg installations found. Streaming functionality will not work!")

app = FastAPI(title="Livestream Backend", version="0.1.0")

# Mount the directory for serving HLS stream files
app.mount("/streams", StaticFiles(directory=STREAMS_BASE_DIR), name="streams")

# CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(overlays.router, prefix="/api")
app.include_router(docs.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
