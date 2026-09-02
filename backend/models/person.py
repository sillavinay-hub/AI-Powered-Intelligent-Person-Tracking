import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database.session import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    person_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. P001
    full_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    reference_image_path = Column(String(255), nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False) # ACTIVE, INACTIVE
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    embeddings = relationship("PersonEmbedding", back_populates="person", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="person", cascade="all, delete-orphan")
    movements = relationship("MovementHistory", back_populates="person", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="person", cascade="all, delete-orphan")

    def to_dict(self, include_embeddings: bool = False):
        data = {
            "id": self.id,
            "person_code": self.person_code,
            "full_name": self.full_name,
            "notes": self.notes,
            "reference_image_path": self.reference_image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_embeddings:
            data["embeddings"] = [e.to_dict() for e in self.embeddings]
        return data

class PersonEmbedding(Base):
    __tablename__ = "person_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    embedding_type = Column(String(20), nullable=False) # FACE, REID
    vector_json = Column(Text, nullable=False) # JSON encoded list of floats (512-D)
    quality_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    person = relationship("Person", back_populates="embeddings")

    def get_vector(self) -> list:
        try:
            return json.loads(self.vector_json)
        except Exception:
            return []

    def set_vector(self, vec: list):
        self.vector_json = json.dumps([float(x) for x in vec])

    def to_dict(self):
        # NOTE: For security/privacy, we do NOT expose the raw 512-D vector over API
        return {
            "id": self.id,
            "person_id": self.person_id,
            "embedding_type": self.embedding_type,
            "quality_score": self.quality_score,
            "dimension": len(self.get_vector()),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MovementHistory(Base):
    __tablename__ = "movement_history"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    duration_sec = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)

    person = relationship("Person", back_populates="movements")
    camera = relationship("Camera")

    def to_dict(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "person_code": self.person.person_code if self.person else None,
            "camera_id": self.camera_id,
            "camera_code": self.camera.camera_code if self.camera else None,
            "camera_name": self.camera.name if self.camera else None,
            "location": self.camera.location if self.camera else None,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "duration_sec": self.duration_sec,
            "confidence": round(self.confidence, 3)
        }
