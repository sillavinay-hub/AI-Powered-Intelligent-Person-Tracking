from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.detection import Detection
from backend.schemas.detection import DetectionResponse
from backend.workers.stream_manager import stream_manager

router = APIRouter(prefix="/api/detections", tags=["Detections"])

@router.get("", response_model=List[DetectionResponse])
def get_recent_detections(
    camera_id: Optional[int] = Query(None),
    person_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    q = db.query(Detection)
    if camera_id:
        q = q.filter(Detection.camera_id == camera_id)
    if person_id:
        q = q.filter(Detection.person_id == person_id)

    records = q.order_by(Detection.timestamp.desc()).limit(limit).all()
    return [r.to_dict() for r in records]

@router.get("/active-live")
def get_active_live_detections():
    """
    Returns instant snapshot of currently active local tracks across all 25 cameras
    directly from stream memory.
    """
    snapshot = {}
    with stream_manager.lock:
        for cam_id, overlays in stream_manager.latest_ai_overlays.items():
            snapshot[cam_id] = overlays
    return snapshot
