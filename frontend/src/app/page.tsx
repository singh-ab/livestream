"use client";
import React, { useState } from "react";
import HlsPlayer from "../components/HlsPlayer";
import OverlayManager from "../components/OverlayManager";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [rtspUrl, setRtspUrl] = useState("");
  const [streamId, setStreamId] = useState("camera-main");
  const [hlsUrl, setHlsUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoWidth, setVideoWidth] = useState(640);
  const [videoHeight, setVideoHeight] = useState(360);

  const handleStartStream = async () => {
    if (!rtspUrl) {
      setError("RTSP URL cannot be empty.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setHlsUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/streams/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stream_id: streamId, rtsp_url: rtspUrl }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to start stream");
      }

      const data = await response.json();
      // Use a timeout to give FFmpeg time to generate the first segments
      setTimeout(() => {
        setHlsUrl(API_BASE_URL + data.hls_url);
        setIsLoading(false);
      }, 3000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred."
      );
      setIsLoading(false);
    }
  };

  return (
    <main
      style={{
        padding: "2rem",
        fontFamily: "sans-serif",
        maxWidth: "960px",
        margin: "auto",
      }}
    >
      <h1>Livestream Viewer</h1>
      <div style={{ display: "flex", gap: "8px", marginBottom: "1rem" }}>
        <input
          style={{ flexGrow: 1, padding: "8px" }}
          placeholder="Enter RTSP URL (e.g., rtsp://...)"
          value={rtspUrl}
          onChange={(e) => setRtspUrl(e.target.value)}
          disabled={isLoading}
        />
        <button onClick={handleStartStream} disabled={isLoading}>
          {isLoading ? "Loading..." : "Load Stream"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div
        style={{
          border: "1px solid #ccc",
          width: "100%",
          aspectRatio: "16 / 9",
          backgroundColor: "#000",
          position: "relative", // Important for absolute positioned overlays
        }}
        ref={(el) => {
          if (el) {
            setVideoWidth(el.clientWidth);
            setVideoHeight(el.clientHeight);
          }
        }}
      >
        {hlsUrl && <HlsPlayer src={hlsUrl} />}
        {!hlsUrl && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#777",
            }}
          >
            {isLoading ? "Starting stream..." : "Stream will appear here"}
          </div>
        )}
      </div>

      {/* Overlay Manager */}
      {hlsUrl && (
        <OverlayManager
          apiUrl={API_BASE_URL}
          containerWidth={videoWidth}
          containerHeight={videoHeight}
          onError={(msg) => setError(msg)}
        />
      )}
    </main>
  );
}
