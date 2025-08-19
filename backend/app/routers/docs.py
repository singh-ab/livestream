from fastapi import APIRouter

router = APIRouter(prefix="/docs-meta", tags=["docs"])

@router.get("/endpoints")
async def list_basic():
    return {
        "overlays": {
            "list": "GET /api/overlays",
            "create": "POST /api/overlays",
            "get": "GET /api/overlays/{id}",
            "update": "PUT /api/overlays/{id}",
            "delete": "DELETE /api/overlays/{id}"
        }
    }
