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
        # Read stderr line by line (already decoded because text=True)
        while True:
            line = process.stderr.readline()
            if not line:
                break
            logger.info(f"[ffmpeg_{stream_id}]: {line.strip()}")
        
        # Wait for process to complete
        process.wait()
        logger.info(f"FFmpeg process for stream '{stream_id}' has ended with return code {process.returncode}")
    except Exception as e:
        logger.error(f"Error monitoring FFmpeg process: {e}", exc_info=True)

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

    # Convert Windows paths to forward slashes for FFmpeg compatibility
    ffmpeg_output_dir = output_dir.replace("\\", "/")
    ffmpeg_playlist = hls_playlist.replace("\\", "/")
    
    # Revised transcode command: enforce constant frame rate & keyframes, remove deletion for debugging
    # Rationale:
    # - Removed -use_wallclock_as_timestamps (was producing huge start PTS)
    # - Force CFR (-r 25) so timestamps advance predictably
    # - Force keyframes every 2s via GOP + force_key_frames expression
    # - Removed delete_segments & temp_file to observe playlist growth while debugging
    # - Added -flush_packets 1 and -max_delay 0 to push data sooner
    # - Keep report for diagnostics
    forced_fps = os.environ.get("HLS_FPS", "25")
    segment_seconds = os.environ.get("HLS_SEG_TIME", "2")
    gop = str(int(int(forced_fps) * int(segment_seconds)))  # frames per segment
    command = [
        "ffmpeg",
        "-report",
        "-hide_banner",
        "-loglevel", "info",
        "-stats_period", "1",
        "-rtsp_transport", "tcp",
        "-fflags", "+genpts+discardcorrupt",
        "-analyzeduration", "500000",
        "-probesize", "500000",
        "-i", rtsp_url,
        # Video
        "-r", forced_fps,              # enforce CFR output
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-g", gop,
        "-keyint_min", gop,
        "-sc_threshold", "0",
        "-force_key_frames", f"expr:gte(t,n_forced*{segment_seconds})",
        "-pix_fmt", "yuv420p",
        "-vf", "format=yuv420p",
        # Audio
        "-c:a", "aac",
        "-b:a", "128k",
        # Output / mux tuning
        "-flush_packets", "1",
        "-max_delay", "0",
        "-f", "hls",
        "-hls_time", segment_seconds,
        "-hls_list_size", "10",
        "-hls_flags", "independent_segments+program_date_time",
        "-hls_allow_cache", "0",
        "-hls_segment_type", "mpegts",
        "-hls_segment_filename", f"{ffmpeg_output_dir}/segment_%d.ts",
        "-master_pl_name", "master.m3u8",
        "-y",
        ffmpeg_playlist,
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
        
        logger.info(f"Started FFmpeg (transcode CFR) for stream '{stream_id}' with PID {process.pid}")

        # Monitor playlist/segments availability & detect stall
        import time
        playlist_created = False
        last_size = -1
        last_mtime = 0
        stalled_checks = 0
        for i in range(60):  # allow up to 60s initial ramp
            await asyncio.sleep(1)
            if process.poll() is not None:
                logger.error(f"FFmpeg exited early (rc={process.returncode}) before playlist creation")
                break
            if os.path.exists(hls_playlist):
                sz = os.path.getsize(hls_playlist)
                mtime = os.path.getmtime(hls_playlist)
                if sz > 0 and not playlist_created:
                    playlist_created = True
                    logger.info(f"HLS playlist file created (size={sz})")
                    try:
                        with open(hls_playlist, 'r') as f:
                            logger.info(f"Initial playlist head:\n{f.read(500)}")
                    except Exception as e:
                        logger.warning(f"Playlist read error: {e}")
                # Detect if playlist stops growing for >10 consecutive checks after creation
                if playlist_created:
                    if (sz == last_size) and (mtime == last_mtime):
                        stalled_checks += 1
                    else:
                        stalled_checks = 0
                    last_size = sz
                    last_mtime = mtime
                    if stalled_checks >= 10:  # ~10s stall
                        logger.error("Detected playlist stall (no change 10s). Restarting FFmpeg process.")
                        try:
                            process.terminate()
                        except Exception:
                            pass
                        # Recursive restart attempt once
                        _active_streams.pop(stream_id, None)
                        return await start_stream(stream_id, rtsp_url)
            if i in (5, 10, 20, 30, 45):
                segs = []
                if os.path.exists(output_dir):
                    for f in sorted(os.listdir(output_dir)):
                        if f.startswith('segment_') and f.endswith('.ts'):
                            segs.append(f)
                logger.info(f"[t+{i}s] segments: {segs[-6:]} (total {len(segs)}) playlist_created={playlist_created}")
            if playlist_created and stalled_checks == 0 and i >= 15:
                # Good steady state; break out early
                break
        if not playlist_created:
            logger.error("Playlist still not created after 60s window.")
            try:
                report_files = [f for f in os.listdir('.') if f.startswith('ffmpeg') and f.endswith('.log')]
                logger.error(f"FFmpeg reports present: {report_files}")
            except Exception:
                pass
        
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
