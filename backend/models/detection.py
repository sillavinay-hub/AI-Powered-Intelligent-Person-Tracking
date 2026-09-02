from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database.session import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    local_track_id = Column(Integer, nullable=False) # Local tracking ID from ByteTrack
    global_person_id = Column(String(50), nullable=True) # e.g. P001 or UNKNOWN
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    # Bounding Box normalized [0, 1] or pixel coords
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    
    # Explainable Multimodal Scores
    face_similarity = Column(Float, default=0.0)
    reid_similarity = Column(Float, default=0.0)
    temporal_score = Column(Float, default=0.0)
    camera_score = Column(Float, default=0.0)
    final_identity_score = Column(Float, default=0.0)
    is_matched = Column(Boolean, default=False)

    camera = relationship("Camera", back_populates="detections")
    person = relationship("Person", back_populates="detections")

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "camera_code": self.camera.camera_code if self.camera else None,
            "camera_name": self.camera.name if self.camera else None,
            "location": self.camera.location if self.camera else None,
            "person_id": self.person_id,
            "local_track_id": self.local_track_id,
            "global_person_id": self.global_person_id or "UNKNOWN",
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bbox": {
                "x": self.bbox_x,
                "y": self.bbox_y,
                "w": self.bbox_width,
                "h": self.bbox_height
            },
            "scores": {
                "face": round(self.face_similarity, 3),
                "reid": round(self.reid_similarity, 3),
                "temporal": round(self.temporal_score, 3),
                "camera": round(self.camera_score, 3),
                "final": round(self.final_identity_score, 3)
            },
            "is_matched": self.is_matched
        }

class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    current_camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    predicted_camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    probability = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    person = relationship("Person")
    current_camera = relationship("Camera", foreign_keys=[current_camera_id])
    predicted_camera = relationship("Camera", foreign_keys=[predicted_camera_id])

    def to_dict(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "person_code": self.person.person_code if self.person else None,
            "current_camera": self.current_camera.camera_code if self.current_camera else None,
            "predicted_camera": self.predicted_camera.camera_code if self.predicted_camera else None,
            "predicted_location": self.predicted_camera.location if self.predicted_camera else None,
            "probability": round(self.probability, 3),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
