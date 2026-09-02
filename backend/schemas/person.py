from typing import Optional, List
from pydantic import BaseModel

class PersonBase(BaseModel):
    person_code: str
    full_name: Optional[str] = None
    notes: Optional[str] = None
    status: str = "ACTIVE"

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class PersonEmbeddingInfo(BaseModel):
    id: int
    embedding_type: str
    quality_score: float
    dimension: int
    created_at: Optional[str] = None

class PersonResponse(PersonBase):
    id: int
    reference_image_path: Optional[str] = None
    created_at: Optional[str] = None
    embeddings: List[PersonEmbeddingInfo] = []
    last_camera_code: Optional[str] = None
    last_location: Optional[str] = None
    last_seen_time: Optional[str] = None
    total_detections: int = 0

    class Config:
        from_attributes = True

class RegistrationResponse(BaseModel):
    person_id: int
    person_code: str
    full_name: Optional[str] = None
    status: str
    face_detected: bool
    face_quality_score: float
    reid_extracted: bool
    message: str
