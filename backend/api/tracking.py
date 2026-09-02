from fastapi import APIRouter
from backend.workers.stream_manager import stream_manager

router = APIRouter(prefix="/api/tracking", tags=["Tracking"])

@router.get("/status")
def get_tracking_status():
    total_active_tracks = 0
    camera_track_summary = {}

    with stream_manager.lock:
        for cam_id, overlays in stream_manager.latest_ai_overlays.items():
            count = len(overlays)
            total_active_tracks += count
            camera_track_summary[cam_id] = {
                "tracks_count": count,
                "identities": [o["global_person_id"] for o in overlays]
            }

    return {
        "is_ai_running": stream_manager.is_ai_running,
        "total_active_tracks": total_active_tracks,
        "camera_track_summary": camera_track_summary
    }
