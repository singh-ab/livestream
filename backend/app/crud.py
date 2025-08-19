from typing import List, Optional
from .models import OverlayCreate, OverlayUpdate, OverlayDB
from uuid import uuid4
import os
from .db import get_overlays_collection
from bson import ObjectId

# In-memory fallback store
_STORE: dict[str, OverlayDB] = {}

USE_DB = os.getenv("USE_MONGO", "0") == "1"


async def _to_db_model(doc) -> OverlayDB:
    return OverlayDB(
        id=str(doc.get("_id")) if doc.get("_id") else doc.get("id"),
        kind=doc["kind"],
        content=doc["content"],
        x=doc.get("x", 0),
        y=doc.get("y", 0),
        width=doc.get("width"),
        height=doc.get("height"),
        opacity=doc.get("opacity", 1.0),
    )


async def create_overlay(data: OverlayCreate) -> OverlayDB:
    if USE_DB:
        col = await get_overlays_collection()
        doc = data.model_dump()
        res = await col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return await _to_db_model(doc)
    oid = str(uuid4())
    overlay = OverlayDB(id=oid, **data.model_dump())
    _STORE[oid] = overlay
    return overlay


async def list_overlays() -> List[OverlayDB]:
    if USE_DB:
        col = await get_overlays_collection()
        docs = col.find({})
        result: List[OverlayDB] = []
        async for d in docs:
            result.append(await _to_db_model(d))
        return result
    return list(_STORE.values())


async def get_overlay(overlay_id: str) -> Optional[OverlayDB]:
    if USE_DB:
        col = await get_overlays_collection()
        try:
            oid = ObjectId(overlay_id)
        except Exception:
            return None
        doc = await col.find_one({"_id": oid})
        if not doc:
            return None
        return await _to_db_model(doc)
    return _STORE.get(overlay_id)


async def update_overlay(overlay_id: str, data: OverlayUpdate) -> Optional[OverlayDB]:
    if USE_DB:
        col = await get_overlays_collection()
        try:
            oid = ObjectId(overlay_id)
        except Exception:
            return None
        updated_fields = data.model_dump()
        res = await col.update_one({"_id": oid}, {"$set": updated_fields})
        if res.matched_count == 0:
            return None
        doc = await col.find_one({"_id": oid})
        return await _to_db_model(doc)
    if overlay_id not in _STORE:
        return None
    updated = OverlayDB(id=overlay_id, **data.model_dump())
    _STORE[overlay_id] = updated
    return updated


async def delete_overlay(overlay_id: str) -> bool:
    if USE_DB:
        col = await get_overlays_collection()
        try:
            oid = ObjectId(overlay_id)
        except Exception:
            return False
        res = await col.delete_one({"_id": oid})
        return res.deleted_count == 1
    return _STORE.pop(overlay_id, None) is not None
