# Livestream Backend

FastAPI backend providing:

- RTSP -> HLS stream management (planned)
- CRUD API for overlay configurations

## Run (development)

```bash
uvicorn app.main:app --reload
```

## Environment Variables

Create a `.env` file:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=livestream
```

## Tests

```bash
pytest
```
