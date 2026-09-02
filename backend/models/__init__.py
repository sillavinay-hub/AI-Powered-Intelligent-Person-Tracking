from backend.database.session import Base
from backend.models.user import User
from backend.models.camera import Camera, CameraTransition
from backend.models.person import Person, PersonEmbedding, MovementHistory
from backend.models.detection import Detection, PredictionResult
from backend.models.alert import Alert
from backend.models.log import SystemLog

__all__ = [
    "Base",
    "User",
    "Camera",
    "CameraTransition",
    "Person",
    "PersonEmbedding",
    "MovementHistory",
    "Detection",
    "PredictionResult",
    "Alert",
    "SystemLog"
]
