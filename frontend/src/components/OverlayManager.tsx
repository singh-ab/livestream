"use client";
import React, { useState, useRef } from "react";
import Draggable from "react-draggable";

interface Overlay {
  id: string;
  kind: string;
  content: string;
  x: number;
  y: number;
  opacity: number;
  width?: number;
  height?: number;
}

interface OverlayManagerProps {
  apiUrl: string;
  containerWidth: number;
  containerHeight: number;
  onError: (message: string) => void;
}

export default function OverlayManager({
  apiUrl,
  containerWidth,
  containerHeight,
  onError,
}: OverlayManagerProps) {
  const [overlays, setOverlays] = useState<Overlay[]>([]);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [newOverlayText, setNewOverlayText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const nextId = useRef(1);

  // Fetch existing overlays from the backend
  const fetchOverlays = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/overlays`);
      if (!response.ok) throw new Error("Failed to fetch overlays");
      const data = await response.json();
      setOverlays(data);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Failed to load overlays");
    } finally {
      setIsLoading(false);
    }
  };

  // Add a new text overlay
  const addTextOverlay = async () => {
    if (!newOverlayText.trim()) return;

    const newOverlay = {
      kind: "text",
      content: newOverlayText,
      x: Math.floor(Math.random() * (containerWidth - 100)),
      y: Math.floor(Math.random() * (containerHeight - 50)),
      opacity: 1.0,
    };

    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/overlays`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newOverlay),
      });

      if (!response.ok) throw new Error("Failed to create overlay");
      const savedOverlay = await response.json();

      setOverlays([...overlays, savedOverlay]);
      setNewOverlayText("");
    } catch (err) {
      onError(err instanceof Error ? err.message : "Failed to add overlay");
    } finally {
      setIsLoading(false);
    }
  };

  // Update an overlay's position
  const updatePosition = (id: string, x: number, y: number) => {
    const overlay = overlays.find((o) => o.id === id);
    if (!overlay) return;

    const updatedOverlay = { ...overlay, x, y };

    // Update locally immediately for responsive UI
    setOverlays(overlays.map((o) => (o.id === id ? { ...o, x, y } : o)));

    // Then update in backend
    fetch(`${apiUrl}/api/overlays/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedOverlay),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed to update overlay position");
        return response.json();
      })
      .catch((err) => {
        onError(
          err instanceof Error ? err.message : "Failed to update overlay"
        );
        // Revert to original state on error
        fetchOverlays();
      });
  };

  // Delete an overlay
  const deleteOverlay = async (id: string) => {
    try {
      const response = await fetch(`${apiUrl}/api/overlays/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete overlay");
      setOverlays(overlays.filter((o) => o.id !== id));
    } catch (err) {
      onError(err instanceof Error ? err.message : "Failed to delete overlay");
    }
  };

  // Load overlays on initial render
  React.useEffect(() => {
    fetchOverlays();
  }, [apiUrl]);

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Overlay Management</h3>

      {/* Add new overlay form */}
      <div style={{ marginBottom: "15px", display: "flex", gap: "8px" }}>
        <input
          style={{ flexGrow: 1, padding: "8px" }}
          placeholder="Enter overlay text"
          value={newOverlayText}
          onChange={(e) => setNewOverlayText(e.target.value)}
          disabled={isLoading}
        />
        <button
          onClick={addTextOverlay}
          disabled={isLoading || !newOverlayText.trim()}
        >
          Add Overlay
        </button>
      </div>

      {/* Overlay list */}
      <div style={{ marginBottom: "15px" }}>
        <h4>Active Overlays</h4>
        {overlays.length === 0 && <p>No overlays added yet.</p>}
        <ul style={{ listStyleType: "none", padding: 0 }}>
          {overlays.map((overlay) => (
            <li
              key={overlay.id}
              style={{
                margin: "8px 0",
                padding: "8px",
                background: "#f5f5f5",
                borderRadius: "4px",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <div>
                <strong>{overlay.content}</strong>
                <div>
                  Position: x={overlay.x}, y={overlay.y}
                </div>
              </div>
              <button
                style={{
                  background: "#ff4d4f",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  padding: "4px 8px",
                }}
                onClick={() => deleteOverlay(overlay.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Draggable overlays */}
      {overlays.map((overlay) => (
        <Draggable
          key={overlay.id}
          defaultPosition={{ x: overlay.x, y: overlay.y }}
          bounds="parent"
          onStop={(e, data) => updatePosition(overlay.id, data.x, data.y)}
        >
          <div
            style={{
              position: "absolute",
              cursor: "move",
              userSelect: "none",
              background: "rgba(255, 255, 255, 0.5)",
              padding: "4px",
              borderRadius: "2px",
              fontSize: "16px",
              opacity: overlay.opacity,
              zIndex: 100,
            }}
          >
            {overlay.content}
          </div>
        </Draggable>
      ))}
    </div>
  );
}
