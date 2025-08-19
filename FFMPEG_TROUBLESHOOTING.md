# FFmpeg Troubleshooting Guide

If you're experiencing issues with FFmpeg in the Livestream Application, follow these steps to resolve them.

## Check If FFmpeg Is Installed

1. Open a terminal/command prompt and run:
   ```
   ffmpeg -version
   ```
   
2. If you get a "command not found" error, FFmpeg is not in your PATH.

## Install FFmpeg

### Windows:

1. Download FFmpeg from the official website: https://ffmpeg.org/download.html
   - Choose one of these builds:
     - [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases)
     - [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (recommended - download "ffmpeg-git-full.7z")

2. Extract the downloaded archive to a location of your choice (e.g., `C:\ffmpeg`)

3. **Important**: Add FFmpeg to your PATH
   - Right-click on "This PC" or "My Computer" → Properties
   - Click on "Advanced system settings"
   - Click the "Environment Variables" button
   - Under "System variables", find and select the "Path" variable
   - Click "Edit"
   - Click "New" and add the path to the bin folder (e.g., `C:\ffmpeg\bin`)
   - Click "OK" on all dialogs

### macOS:

```bash
brew install ffmpeg
```

### Linux:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Configure the Application to Find FFmpeg

If FFmpeg is installed but the application can't find it, you can:

### Option 1: Restart After Adding to PATH

If you've added FFmpeg to your PATH, restart your terminal and the application.

### Option 2: Set the FFMPEG_PATH Environment Variable

1. Find the full path to your FFmpeg executable (e.g., `C:\ffmpeg\bin\ffmpeg.exe`)

2. Set the environment variable before starting the server:

   **Windows (PowerShell):**
   ```powershell
   $env:FFMPEG_PATH="C:\path\to\ffmpeg.exe"
   uvicorn app.main:app --reload
   ```

   **Windows (Command Prompt):**
   ```cmd
   set FFMPEG_PATH=C:\path\to\ffmpeg.exe
   uvicorn app.main:app --reload
   ```

   **macOS/Linux:**
   ```bash
   export FFMPEG_PATH=/path/to/ffmpeg
   uvicorn app.main:app --reload
   ```

### Option 3: Use the FFmpeg Finder Tool

The application includes a tool to help find FFmpeg installations:

```bash
python app/ffmpeg_finder.py
```

This will print any FFmpeg installations it finds and suggest the correct FFMPEG_PATH setting.

## Testing Your RTSP URL

To verify your RTSP URL works with FFmpeg, try:

```bash
ffmpeg -i rtsp://your-rtsp-url -t 5 -c copy test.mp4
```

This attempts to record 5 seconds from your RTSP stream. If this works but the application still fails, there may be other issues with the application configuration.

## Common Issues

1. **VLC player can play an RTSP URL but FFmpeg can't**:
   - Some RTSP servers require specific options. Try adding these FFmpeg options:
     ```
     ffmpeg -rtsp_transport tcp -i rtsp://your-url ...
     ```

2. **Authentication required**:
   - If your RTSP stream requires authentication, use:
     ```
     ffmpeg -i rtsp://username:password@your-url ...
     ```

3. **FFmpeg is found but fails to process the stream**:
   - Check the detailed logs in your terminal
   - Try different FFmpeg options or codecs
   - Verify the RTSP URL is accessible from your server

If you continue experiencing issues, check the application logs for more details.
