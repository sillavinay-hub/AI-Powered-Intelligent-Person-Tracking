from typing import Optional, List, Any
from pydantic import BaseModel
from backend.schemas.detection import DetectionResponse, MovementTimelineItem

class StructuredSearchQuery(BaseModel):
    person_code: Optional[str] = None
    camera_id: Optional[int] = None
    camera_code: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    min_confidence: Optional[float] = None
    limit: int = 50

class NaturalLanguageQuery(BaseModel):
    query: str

class NLQueryResult(BaseModel):
    query: str
    interpreted_intent: str
    parsed_parameters: dict
    summary: str
    results: List[Any] = []

class SearchSummaryResponse(BaseModel):
    person_code: Optional[str] = None
    last_detected_camera: Optional[str] = None
    last_detected_location: Optional[str] = None
    last_detected_time: Optional[str] = None
    total_detections: int = 0
    records: List[DetectionResponse] = []
