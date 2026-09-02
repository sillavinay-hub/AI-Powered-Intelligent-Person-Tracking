import cv2
import time
import base64
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.camera import Camera, CameraTransition
from backend.schemas.camera import CameraCreate, CameraUpdate
from backend.ai.stream.camera_source import CameraSource
from backend.utils.logger import logger

class CameraService:
    def get_all_cameras(self, db: Session) -> List[Camera]:
        return db.query(Camera).order_by(Camera.id.asc()).all()

    def get_camera_by_id(self, camera_id: int, db: Session) -> Camera:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if not cam:
            raise HTTPException(status_code=404, detail=f"Camera ID {camera_id} not found.")
        return cam

    def get_camera_by_code(self, camera_code: str, db: Session) -> Camera:
        cam = db.query(Camera).filter(Camera.camera_code == camera_code.upper()).first()
        if not cam:
            raise HTTPException(status_code=404, detail=f"Camera code {camera_code} not found.")
        return cam

    def create_camera(self, camera_in: CameraCreate, db: Session) -> Camera:
        existing = db.query(Camera).filter(Camera.camera_code == camera_in.camera_code).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Camera code {camera_in.camera_code} already exists.")

        cam = Camera(
            camera_code=camera_in.camera_code.upper(),
            name=camera_in.name,
            location=camera_in.location,
            rtsp_url=camera_in.rtsp_url,
            source_type=camera_in.source_type,
            video_file_path=camera_in.video_file_path,
            map_x=camera_in.map_x,
            map_y=camera_in.map_y,
            latitude=camera_in.latitude,
            longitude=camera_in.longitude,
            status=camera_in.status,
            ai_enabled=camera_in.ai_enabled,
            fps=camera_in.fps
        )
        db.add(cam)
        db.commit()
        db.refresh(cam)
        logger.info(f"Created new camera: {cam.camera_code} - {cam.name}")
        return cam

    def update_camera(self, camera_id: int, camera_in: CameraUpdate, db: Session) -> Camera:
        cam = self.get_camera_by_id(camera_id, db)
        update_data = camera_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cam, field, value)

        db.commit()
        db.refresh(cam)
        logger.info(f"Updated camera: {cam.camera_code}")
        return cam

    def delete_camera(self, camera_id: int, db: Session) -> bool:
        cam = self.get_camera_by_id(camera_id, db)
        db.delete(cam)
        db.commit()
        logger.info(f"Deleted camera ID {camera_id}")
        return True

    def test_camera(self, camera_id: int, db: Session) -> Dict[str, Any]:
        """
        Tests connection to camera stream, measures round-trip latency,
        and returns a base64-encoded snapshot preview frame.
        """
        cam = self.get_camera_by_id(camera_id, db)
        start_t = time.time()

        source = CameraSource(
            camera_id=cam.id,
            camera_code=cam.camera_code,
            name=cam.name,
            location=cam.location,
            source_type=cam.source_type,
            rtsp_url=cam.rtsp_url,
            video_file_path=cam.video_file_path,
            fps=cam.fps
        )
        source.start()
        time.sleep(0.15) # Wait for initial frame capture
        success, frame = source.read_frame()
        latency_ms = (time.time() - start_t) * 1000.0
        source.stop()

        if success and frame is not None:
            # Encode frame to JPEG then base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            b64_str = base64.b64encode(buffer).decode('utf-8')
            return {
                "camera_id": cam.id,
                "camera_code": cam.camera_code,
                "status": "ONLINE",
                "latency_ms": round(latency_ms, 1),
                "message": f"Successfully connected to {cam.camera_code} ({cam.source_type}).",
                "frame_preview_base64": f"data:image/jpeg;base64,{b64_str}"
            }
        else:
            return {
                "camera_id": cam.id,
                "camera_code": cam.camera_code,
                "status": "ERROR",
                "latency_ms": round(latency_ms, 1),
                "message": f"Failed to acquire video frame from {cam.camera_code}.",
                "frame_preview_base64": None
            }

camera_service = CameraService()
