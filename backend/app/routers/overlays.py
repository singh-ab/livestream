from fastapi import APIRouter, HTTPException
from typing import List
from ..models import OverlayCreate, OverlayUpdate, OverlayDB
from .. import crud

router = APIRouter(prefix="/overlays", tags=["overlays"])

@router.post("", response_model=OverlayDB)
async def create_overlay(payload: OverlayCreate):
    return await crud.create_overlay(payload)

@router.get("", response_model=List[OverlayDB])
async def list_overlays():
    return await crud.list_overlays()

@router.get("/{overlay_id}", response_model=OverlayDB)
async def get_overlay(overlay_id: str):
    ov = await crud.get_overlay(overlay_id)
    if not ov:
        raise HTTPException(status_code=404, detail="Overlay not found")
    return ov

@router.put("/{overlay_id}", response_model=OverlayDB)
async def update_overlay(overlay_id: str, payload: OverlayUpdate):
    updated = await crud.update_overlay(overlay_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Overlay not found")
    return updated

@router.delete("/{overlay_id}")
async def delete_overlay(overlay_id: str):
    ok = await crud.delete_overlay(overlay_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Overlay not found")
    return {"ok": True}
