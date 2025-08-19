import asyncio
import os
import shutil
import subprocess
import threading
from dataclasses import dataclass
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StreamProcess:
    rtsp_url: str
    process: subprocess.Popen
    output_dir: str
    thread: threading.Thread

# In-memory store for active stream processes
_active_streams: Dict[str, StreamProcess] = {}
STREAMS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "streams"))

def get_stream_output_dir(stream_id: str) -> str:
    return os.path.join(STREAMS_BASE_DIR, stream_id)

def _monitor_process(process: subprocess.Popen, stream_id: str):
    """Monitor FFmpeg process output in a separate thread."""
    try:
        # Read stderr line by line
        while True:
            line = process.stderr.readline()
            if not line:
                break
            logger.info(f"[ffmpeg_{stream_id}]: {line.decode().strip()}")
        
        # Wait for process to complete
        process.wait()
        logger.info(f"FFmpeg process for stream '{stream_id}' has ended with return code {process.returncode}")
    except Exception as e:
        logger.error(f"Error monitoring FFmpeg process: {e}")

async def start_stream(stream_id: str, rtsp_url: str) -> Optional[str]:
    """
    Starts an FFmpeg process to convert an RTSP stream to HLS.
    Returns the HLS playlist URL if successful, otherwise None.
    """
    if stream_id in _active_streams:
        logger.warning(f"Stream '{stream_id}' is already running.")
        return None

    output_dir = get_stream_output_dir(stream_id)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Ensure the output directory exists
    logger.info(f"Output directory: {output_dir}")
    hls_playlist = os.path.join(output_dir, "index.m3u8")
    logger.info(f"HLS playlist path: {hls_playlist}")

    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",  # Use TCP for RTSP transport
        "-i", rtsp_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "hls",
        "-hls_time", "4",
        "-hls_list_size", "5",
        "-hls_flags", "delete_segments",
        hls_playlist,
    ]

    logger.info(f"Starting FFmpeg with command: {' '.join(command)}")
    
    # Test if ffmpeg is accessible using regular subprocess
    try:
        logger.info("Testing FFmpeg accessibility...")
        test_process = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if test_process.returncode == 0:
            logger.info("FFmpeg is accessible")
            logger.info(f"FFmpeg version info: {test_process.stdout[:200]}...")  # First 200 chars
        else:
            logger.error(f"FFmpeg test failed with return code {test_process.returncode}")
            logger.error(f"FFmpeg stderr: {test_process.stderr}")
            return None
    except FileNotFoundError as e:
        logger.error(f"FFmpeg not found in PATH: {e}")
        logger.info(f"Current PATH: {os.environ.get('PATH', 'Not found')}")
        return None
    except Exception as e:
        logger.error(f"FFmpeg test failed: {type(e).__name__}: {e}", exc_info=True)
        return None
    
    try:
        # Start FFmpeg process using regular subprocess (Windows compatible)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=_monitor_process,
            args=(process, stream_id),
            daemon=True
        )
        monitor_thread.start()

        _active_streams[stream_id] = StreamProcess(
            rtsp_url=rtsp_url,
            process=process,
            output_dir=output_dir,
            thread=monitor_thread
        )
        
        logger.info(f"Started FFmpeg for stream '{stream_id}' with PID {process.pid}")
        # The HLS URL is relative to the static path we will set up
        return f"/streams/{stream_id}/index.m3u8"

    except FileNotFoundError as e:
        logger.error(f"ffmpeg command not found. Please ensure FFmpeg is installed and in your system's PATH. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to start FFmpeg for stream '{stream_id}': {type(e).__name__}: {e}", exc_info=True)
        return None

async def stop_stream(stream_id: str) -> bool:
    """Stops a running FFmpeg process and cleans up its files."""
    stream = _active_streams.pop(stream_id, None)
    if stream:
        logger.info(f"Stopping stream '{stream_id}' (PID: {stream.process.pid})")
        stream.process.terminate()
        stream.process.wait()  # Wait for process to actually terminate
        
        # Clean up the stream directory
        try:
            shutil.rmtree(stream.output_dir)
            logger.info(f"Cleaned up directory: {stream.output_dir}")
        except OSError as e:
            logger.error(f"Error cleaning up directory {stream.output_dir}: {e}")
            
        return True
    return False

def get_active_streams() -> Dict[str, dict]:
    """Returns a dictionary of active streams and their details."""
    return {
        stream_id: {
            "rtsp_url": stream.rtsp_url,
            "pid": stream.process.pid,
            "output_dir": stream.output_dir,
            "hls_url": f"/streams/{stream_id}/index.m3u8"
        }
        for stream_id, stream in _active_streams.items()
    }
