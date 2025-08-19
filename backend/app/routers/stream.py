from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict

from .. import stream_manager

router = APIRouter(prefix="/streams", tags=["streaming"])

class StreamRequest(BaseModel):
    stream_id: str = Field(..., description="A unique identifier for the stream, e.g., 'camera-1'.")
    rtsp_url: str = Field(..., description="The full RTSP URL of the source stream.")

@router.post("/start", status_code=201)
async def start_new_stream(payload: StreamRequest):
    """
    Start a new RTSP to HLS stream conversion.
    """
    hls_url = await stream_manager.start_stream(payload.stream_id, payload.rtsp_url)
    if not hls_url:
        raise HTTPException(
            status_code=500,
            detail="Failed to start stream. Ensure FFmpeg is installed and the RTSP URL is valid."
        )
    return {"stream_id": payload.stream_id, "hls_url": hls_url}

@router.post("/stop/{stream_id}", status_code=200)
async def stop_existing_stream(stream_id: str):
    """
    Stop a running stream conversion.
    """
    success = await stream_manager.stop_stream(stream_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Stream '{stream_id}' not found or already stopped.")
    return {"status": "stopped", "stream_id": stream_id}

@router.get("/active", response_model=Dict[str, dict])
async def get_active_streams():
    """
    Get a list of all currently active streams.
    """
    return stream_manager.get_active_streams()
