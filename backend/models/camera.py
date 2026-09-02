from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.session import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_code = Column(String(20), unique=True, index=True, nullable=False) # e.g. CAM-01
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    rtsp_url = Column(String(255), nullable=True)
    source_type = Column(String(20), default="DEMO", nullable=False) # RTSP, VIDEO_FILE, WEBCAM, DEMO
    video_file_path = Column(String(255), nullable=True)
    
    # 2D Resort Map Coordinates (0-100 percentage or pixel offsets for UI rendering)
    map_x = Column(Float, default=50.0)
    map_y = Column(Float, default=50.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    status = Column(String(20), default="ONLINE", nullable=False) # ONLINE, OFFLINE, PROCESSING, ERROR
    ai_enabled = Column(Boolean, default=True, nullable=False)
    fps = Column(Float, default=10.0)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    detections = relationship("Detection", back_populates="camera", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="camera", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "camera_code": self.camera_code,
            "name": self.name,
            "location": self.location,
            "rtsp_url": self.rtsp_url,
            "source_type": self.source_type,
            "video_file_path": self.video_file_path,
            "map_x": self.map_x,
            "map_y": self.map_y,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "ai_enabled": self.ai_enabled,
            "fps": self.fps,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class CameraTransition(Base):
    __tablename__ = "camera_transitions"

    id = Column(Integer, primary_key=True, index=True)
    from_camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    to_camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    min_duration_sec = Column(Float, default=5.0)
    max_duration_sec = Column(Float, default=300.0)
    transition_probability = Column(Float, default=0.5)

    from_camera = relationship("Camera", foreign_keys=[from_camera_id])
    to_camera = relationship("Camera", foreign_keys=[to_camera_id])

    def to_dict(self):
        return {
            "id": self.id,
            "from_camera_id": self.from_camera_id,
            "to_camera_id": self.to_camera_id,
            "min_duration_sec": self.min_duration_sec,
            "max_duration_sec": self.max_duration_sec,
            "transition_probability": self.transition_probability
        }
