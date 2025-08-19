# API Documentation for Livestream Overlay Application

This document provides detailed information about the API endpoints available in the Livestream Overlay application.

## Base URL

All API endpoints are relative to: `http://localhost:8000/`

## Authentication

Currently, the API does not require authentication.

## Endpoints

### Stream Management

#### Start a Stream

Initiates an RTSP to HLS stream conversion.

- **URL:** `/api/streams/start`
- **Method:** `POST`
- **Content-Type:** `application/json`

**Request Body:**

```json
{
  "stream_id": "unique-stream-identifier",
  "rtsp_url": "rtsp://example.com/stream"
}
```

**Success Response:**

- **Code:** 201 Created
- **Content:**

```json
{
  "stream_id": "unique-stream-identifier",
  "hls_url": "/streams/unique-stream-identifier/index.m3u8"
}
```

**Error Response:**

- **Code:** 500 Internal Server Error
- **Content:**

```json
{
  "detail": "Failed to start stream. Ensure FFmpeg is installed and the RTSP URL is valid."
}
```

#### Stop a Stream

Stops a running RTSP to HLS conversion.

- **URL:** `/api/streams/stop/{stream_id}`
- **Method:** `POST`
- **URL Parameters:** `stream_id` - The unique identifier for the stream

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "status": "stopped",
  "stream_id": "unique-stream-identifier"
}
```

**Error Response:**

- **Code:** 404 Not Found
- **Content:**

```json
{
  "detail": "Stream 'unique-stream-identifier' not found or already stopped."
}
```

#### List Active Streams

Returns a list of all currently active streams.

- **URL:** `/api/streams/active`
- **Method:** `GET`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "unique-stream-identifier": {
    "rtsp_url": "rtsp://example.com/stream",
    "pid": 1234,
    "output_dir": "/app/streams/unique-stream-identifier",
    "hls_url": "/streams/unique-stream-identifier/index.m3u8"
  }
}
```

### Overlay Management

#### Create an Overlay

Creates a new overlay.

- **URL:** `/api/overlays`
- **Method:** `POST`
- **Content-Type:** `application/json`

**Request Body:**

```json
{
  "kind": "text",
  "content": "Hello World",
  "x": 10,
  "y": 20,
  "opacity": 0.8
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "id": "6073a5c27b9f7e3a3e3b8f42",
  "kind": "text",
  "content": "Hello World",
  "x": 10,
  "y": 20,
  "opacity": 0.8
}
```

#### Get All Overlays

Returns a list of all overlays.

- **URL:** `/api/overlays`
- **Method:** `GET`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
  {
    "id": "6073a5c27b9f7e3a3e3b8f42",
    "kind": "text",
    "content": "Hello World",
    "x": 10,
    "y": 20,
    "opacity": 0.8
  }
]
```

#### Get a Specific Overlay

Returns details about a specific overlay.

- **URL:** `/api/overlays/{overlay_id}`
- **Method:** `GET`
- **URL Parameters:** `overlay_id` - The unique identifier for the overlay

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "id": "6073a5c27b9f7e3a3e3b8f42",
  "kind": "text",
  "content": "Hello World",
  "x": 10,
  "y": 20,
  "opacity": 0.8
}
```

**Error Response:**

- **Code:** 404 Not Found
- **Content:**

```json
{
  "detail": "Overlay not found"
}
```

#### Update an Overlay

Updates an existing overlay.

- **URL:** `/api/overlays/{overlay_id}`
- **Method:** `PUT`
- **Content-Type:** `application/json`
- **URL Parameters:** `overlay_id` - The unique identifier for the overlay

**Request Body:**

```json
{
  "kind": "text",
  "content": "Updated Text",
  "x": 30,
  "y": 40,
  "opacity": 0.9
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "id": "6073a5c27b9f7e3a3e3b8f42",
  "kind": "text",
  "content": "Updated Text",
  "x": 30,
  "y": 40,
  "opacity": 0.9
}
```

**Error Response:**

- **Code:** 404 Not Found
- **Content:**

```json
{
  "detail": "Overlay not found"
}
```

#### Delete an Overlay

Deletes an overlay.

- **URL:** `/api/overlays/{overlay_id}`
- **Method:** `DELETE`
- **URL Parameters:** `overlay_id` - The unique identifier for the overlay

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "ok": true
}
```

**Error Response:**

- **Code:** 404 Not Found
- **Content:**

```json
{
  "detail": "Overlay not found"
}
```

## Data Models

### Stream

| Field      | Type   | Description                             |
| ---------- | ------ | --------------------------------------- |
| stream_id  | string | Unique identifier for the stream        |
| rtsp_url   | string | The RTSP URL of the source stream       |
| pid        | number | Process ID of the FFmpeg instance       |
| output_dir | string | Directory where HLS segments are stored |
| hls_url    | string | URL to access the HLS stream            |

### Overlay

| Field   | Type   | Description                                                   |
| ------- | ------ | ------------------------------------------------------------- |
| id      | string | Unique identifier for the overlay                             |
| kind    | string | Type of overlay (e.g., "text", "image")                       |
| content | string | The content of the overlay (text content or image URL/base64) |
| x       | number | X position of the overlay                                     |
| y       | number | Y position of the overlay                                     |
| width   | number | Width of the overlay (optional)                               |
| height  | number | Height of the overlay (optional)                              |
| opacity | number | Opacity of the overlay (0.0 to 1.0)                           |
