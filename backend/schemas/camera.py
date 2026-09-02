from typing import Optional, List
from pydantic import BaseModel

class CameraBase(BaseModel):
    camera_code: str
    name: str
    location: str
    rtsp_url: Optional[str] = None
    source_type: str = "DEMO" # RTSP, VIDEO_FILE, WEBCAM, DEMO
    video_file_path: Optional[str] = None
    map_x: float = 50.0
    map_y: float = 50.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "ONLINE"
    ai_enabled: bool = True
    fps: float = 10.0

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    source_type: Optional[str] = None
    video_file_path: Optional[str] = None
    map_x: Optional[float] = None
    map_y: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    ai_enabled: Optional[bool] = None
    fps: Optional[float] = None

class CameraResponse(CameraBase):
    id: int
    last_heartbeat: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class CameraTransitionCreate(BaseModel):
    from_camera_id: int
    to_camera_id: int
    min_duration_sec: float = 5.0
    max_duration_sec: float = 300.0
    transition_probability: float = 0.5

class CameraTransitionResponse(BaseModel):
    id: int
    from_camera_id: int
    to_camera_id: int
    min_duration_sec: float
    max_duration_sec: float
    transition_probability: float

    class Config:
        from_attributes = True

class CameraTestResponse(BaseModel):
    camera_id: int
    camera_code: str
    status: str
    latency_ms: float
    message: str
    frame_preview_base64: Optional[str] = None
