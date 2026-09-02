from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database.session import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), default="INFO", nullable=False) # INFO, WARNING, ERROR, CRITICAL
    module = Column(String(50), nullable=False) # AUTH, CAMERA, AI, REID, FUSION, ALERT
    message = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
