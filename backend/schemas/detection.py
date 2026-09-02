from typing import Optional, Dict
from pydantic import BaseModel

class BBox(BaseModel):
    x: float
    y: float
    w: float
    h: float

class ScoreBreakdown(BaseModel):
    face: float
    reid: float
    temporal: float
    camera: float
    final: float

class DetectionResponse(BaseModel):
    id: int
    camera_id: int
    camera_code: Optional[str] = None
    camera_name: Optional[str] = None
    location: Optional[str] = None
    person_id: Optional[int] = None
    local_track_id: int
    global_person_id: str
    timestamp: str
    bbox: BBox
    scores: ScoreBreakdown
    is_matched: bool

class MovementTimelineItem(BaseModel):
    id: int
    person_id: int
    person_code: str
    camera_id: int
    camera_code: str
    camera_name: str
    location: str
    entry_time: str
    exit_time: Optional[str] = None
    duration_sec: float
    confidence: float

class PredictionResponse(BaseModel):
    person_id: int
    person_code: str
    current_camera: str
    predicted_camera: str
    predicted_location: str
    probability: float
    timestamp: str
    explanation: str
