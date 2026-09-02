from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False) # RESTRICTED_ZONE, LOITERING, UNUSUAL_TIME, CAMERA_OFFLINE, LOW_AI_CONFIDENCE, IDENTITY_AMBIGUOUS
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    confidence = Column(Float, default=1.0)
    status = Column(String(20), default="NEW", nullable=False) # NEW, ACKNOWLEDGED, RESOLVED
    details_json = Column(Text, nullable=True) # Additional explanation or context

    person = relationship("Person", back_populates="alerts")
    camera = relationship("Camera", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "person_id": self.person_id,
            "person_code": self.person.person_code if self.person else None,
            "camera_id": self.camera_id,
            "camera_code": self.camera.camera_code if self.camera else None,
            "camera_name": self.camera.name if self.camera else None,
            "location": self.camera.location if self.camera else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence": round(self.confidence, 3),
            "status": self.status,
            "details": self.details_json
        }
