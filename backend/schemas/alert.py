from typing import Optional
from pydantic import BaseModel

class AlertCreate(BaseModel):
    alert_type: str
    camera_id: int
    person_id: Optional[int] = None
    confidence: float = 1.0
    details_json: Optional[str] = None

class AlertUpdate(BaseModel):
    status: str # NEW, ACKNOWLEDGED, RESOLVED

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    person_id: Optional[int] = None
    person_code: Optional[str] = None
    camera_id: int
    camera_code: Optional[str] = None
    camera_name: Optional[str] = None
    location: Optional[str] = None
    timestamp: str
    confidence: float
    status: str
    details: Optional[str] = None

    class Config:
        from_attributes = True
