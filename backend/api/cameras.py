from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.camera import CameraCreate, CameraUpdate, CameraResponse, CameraTestResponse
from backend.services.camera_service import camera_service
from backend.services.transition_service import transition_service
from backend.workers.stream_manager import stream_manager
from backend.utils.security import get_current_user, require_admin, require_operator

router = APIRouter(prefix="/api/cameras", tags=["Cameras"])

@router.get("", response_model=List[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    cameras = camera_service.get_all_cameras(db)
    results = []
    for c in cameras:
        d = c.to_dict()
        source = stream_manager.sources.get(c.id)
        if source:
            d["fps"] = round(source.actual_fps, 1) if source.actual_fps > 0 else c.fps
            d["status"] = "ONLINE" if source.is_running else "OFFLINE"
        results.append(d)
    return results

@router.get("/map/graph")
def get_resort_map(db: Session = Depends(get_db)):
    return transition_service.get_map_graph(db)

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = camera_service.get_camera_by_id(camera_id, db)
    d = cam.to_dict()
    source = stream_manager.sources.get(cam.id)
    if source:
        d["fps"] = round(source.actual_fps, 1)
    return d

@router.post("", response_model=CameraResponse)
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    cam = camera_service.create_camera(camera_in, db)
    # Register with stream manager
    stream_manager.initialize_cameras()
    return cam.to_dict()

@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera_in: CameraUpdate, db: Session = Depends(get_db), user=Depends(require_admin)):
    cam = camera_service.update_camera(camera_id, camera_in, db)
    return cam.to_dict()

@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    camera_service.delete_camera(camera_id, db)
    return {"message": f"Camera ID {camera_id} deleted successfully."}

@router.post("/{camera_id}/test", response_model=CameraTestResponse)
def test_camera_connection(camera_id: int, db: Session = Depends(get_db)):
    return camera_service.test_camera(camera_id, db)

@router.get("/{camera_id}/stream")
def stream_camera_feed(camera_id: int):
    """
    Real-time MJPEG live stream with bounding boxes and track overlays.
    """
    if camera_id not in stream_manager.sources:
        stream_manager.initialize_cameras()

    return StreamingResponse(
        stream_manager.generate_mjpeg_stream(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/{camera_id}/snapshot")
def get_camera_snapshot(camera_id: int):
    """
    Returns single latest annotated frame as JPEG.
    High performance, non-blocking, immune to HTTP/1.1 socket limits.
    """
    if camera_id not in stream_manager.sources:
        stream_manager.initialize_cameras()

    jpeg_bytes = stream_manager.get_jpeg_frame(camera_id)
    if not jpeg_bytes:
        raise HTTPException(status_code=404, detail="Camera frame not ready")

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
