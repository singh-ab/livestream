import os
import subprocess
import sys
from typing import Optional, List

def find_ffmpeg_installations() -> List[str]:
    """
    Try to find FFmpeg installations on the system.
    Returns a list of possible paths where FFmpeg is installed.
    """
    paths = []
    
    # Check if FFmpeg is in PATH
    try:
        if sys.platform == "win32":
            result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                paths.extend([p for p in result.stdout.splitlines() if p.strip()])
        else:  # Linux/MacOS
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                paths.append(result.stdout.strip())
    except Exception:
        pass

    # Common installation directories
    if sys.platform == "win32":
        common_dirs = [
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "FFmpeg", "bin"),
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "FFmpeg", "bin"),
            r"C:\FFmpeg\bin",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "FFmpeg", "bin"),
            os.path.join(os.environ.get("APPDATA", ""), "FFmpeg", "bin"),
        ]
        for directory in common_dirs:
            ffmpeg_path = os.path.join(directory, "ffmpeg.exe")
            if os.path.isfile(ffmpeg_path):
                paths.append(ffmpeg_path)

    return paths

def is_ffmpeg_working(ffmpeg_path: str = "ffmpeg") -> bool:
    """
    Check if FFmpeg at the given path is working correctly.
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

if __name__ == "__main__":
    # This allows running this script directly to check FFmpeg
    print("Searching for FFmpeg installations...")
    
    installations = find_ffmpeg_installations()
    
    if installations:
        print(f"Found FFmpeg at the following locations:")
        for path in installations:
            working = is_ffmpeg_working(path)
            status = "WORKING" if working else "NOT WORKING"
            print(f"  - {path} [{status}]")
        
        # Suggest the first working installation
        for path in installations:
            if is_ffmpeg_working(path):
                print(f"\nSuggested FFMPEG_PATH setting:")
                if sys.platform == "win32":
                    print(f'set FFMPEG_PATH="{path}"')
                else:
                    print(f'export FFMPEG_PATH="{path}"')
                break
    else:
        print("No FFmpeg installations found.")
        print("Please install FFmpeg and make sure it's in your PATH or set the FFMPEG_PATH environment variable.")
