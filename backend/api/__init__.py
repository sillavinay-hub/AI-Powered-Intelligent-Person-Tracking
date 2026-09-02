from backend.api.auth import router as auth_router
from backend.api.cameras import router as cameras_router
from backend.api.persons import router as persons_router
from backend.api.detections import router as detections_router
from backend.api.tracking import router as tracking_router
from backend.api.search import router as search_router
from backend.api.timeline import router as timeline_router
from backend.api.alerts import router as alerts_router
from backend.api.analytics import router as analytics_router
from backend.api.predictions import router as predictions_router
from backend.api.experiments import router as experiments_router

__all__ = [
    "auth_router",
    "cameras_router",
    "persons_router",
    "detections_router",
    "tracking_router",
    "search_router",
    "timeline_router",
    "alerts_router",
    "analytics_router",
    "predictions_router",
    "experiments_router"
]
