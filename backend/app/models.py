from pydantic import BaseModel, Field
from typing import Optional

class OverlayBase(BaseModel):
    kind: str = Field(..., description="Type of overlay: text|image")
    content: str = Field(..., description="Text content or image URL/base64")
    x: int = Field(0, ge=0)
    y: int = Field(0, ge=0)
    width: Optional[int] = Field(None, ge=1)
    height: Optional[int] = Field(None, ge=1)
    opacity: float = Field(1.0, ge=0.0, le=1.0)

class OverlayCreate(OverlayBase):
    pass

class OverlayUpdate(OverlayBase):
    pass

class OverlayDB(OverlayBase):
    id: str
