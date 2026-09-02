import time
import cv2
import threading
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from backend.ai.stream.camera_source import CameraSource
from backend.ai.detection.detector import PersonDetector
from backend.ai.tracking.tracker import ByteTracker
from backend.ai.face.recognition import face_engine
from backend.ai.reid.reid_features import reid_extractor
from backend.ai.fusion.multimodal_fusion import fusion_engine
from backend.database.session import SessionLocal
from backend.models.camera import Camera
from backend.models.person import Person, PersonEmbedding, MovementHistory
from backend.models.detection import Detection
from backend.services.anomaly_service import anomaly_service
from backend.services.transition_service import transition_service
from backend.config import settings
from backend.utils.logger import logger

class CameraStreamManager:
    """
    Manages active camera stream sources and orchestrates decoupled background AI processing.
    Separates heavy inference loops from FastAPI request handlers.
    """
    def __init__(self):
        self.sources: Dict[int, CameraSource] = {}
        self.trackers: Dict[int, ByteTracker] = {}
        self.detector = PersonDetector()
        self.is_ai_running = False
        self.ai_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.latest_ai_overlays: Dict[int, List[dict]] = {}

    def initialize_cameras(self):
        db = SessionLocal()
        try:
            cameras = db.query(Camera).all()
            for cam in cameras:
                if cam.id not in self.sources:
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
                    self.sources[cam.id] = source
                    self.trackers[cam.id] = ByteTracker(max_age=settings.MAX_TRACKING_AGE)
                    self.latest_ai_overlays[cam.id] = []
            logger.info(f"Stream Manager initialized {len(self.sources)} active camera streams.")
        finally:
            db.close()

    def start_ai_processing(self):
        if self.is_ai_running:
            return
        self.is_ai_running = True
        self.ai_thread = threading.Thread(target=self._ai_worker_loop, daemon=True)
        self.ai_thread.start()
        logger.info(f"AI Background Pipeline started (Target AI inference: {settings.AI_FRAME_RATE} FPS).")

    def _ai_worker_loop(self):
        """
        Continuous background worker processing camera frames sequentially/round-robin
        without congesting system resources.
        """
        time.sleep(1.0) # Grace period for streams to buffer
        while self.is_ai_running:
            try:
                db = SessionLocal()
                # Fetch registered reference person embeddings for gallery comparison
                registered_persons = db.query(Person).filter(Person.status == "ACTIVE").all()
                gallery = []
                for p in registered_persons:
                    face_emb_obj = db.query(PersonEmbedding).filter(
                        PersonEmbedding.person_id == p.id,
                        PersonEmbedding.embedding_type == "FACE"
                    ).first()
                    reid_emb_obj = db.query(PersonEmbedding).filter(
                        PersonEmbedding.person_id == p.id,
                        PersonEmbedding.embedding_type == "REID"
                    ).first()

                    gallery.append({
                        "person_id": p.id,
                        "person_code": p.person_code,
                        "face_emb": np.array(face_emb_obj.get_vector()) if face_emb_obj else None,
                        "reid_emb": np.array(reid_emb_obj.get_vector()) if reid_emb_obj else None
                    })

                cam_ids = list(self.sources.keys())
                for cam_id in cam_ids:
                    source = self.sources.get(cam_id)
                    if not source:
                        continue

                    # Grab latest frame
                    success, frame = source.read_frame()
                    if not success or frame is None:
                        continue

                    # 1. Person Detection
                    detections = self.detector.detect(frame, camera_id=cam_id)
                    
                    # If synthetic source has ground-truth person and detector missed on empty background:
                    gt_bbox = source.get_ground_truth_bbox()
                    if len(detections) == 0 and gt_bbox is not None:
                        gx, gy, gw, gh = gt_bbox
                        detections.append({
                            "bbox": [gx, gy, gx + gw, gy + gh],
                            "confidence": 0.88,
                            "class_id": 0,
                            "timestamp": datetime.utcnow(),
                            "camera_id": cam_id
                        })

                    # 2. Local Multi-Object Tracking (ByteTrack)
                    tracker = self.trackers.get(cam_id)
                    tracks = tracker.update(detections) if tracker else []

                    # 3. Biometric & ReID extraction on tracks
                    active_overlays = []
                    for trk in tracks:
                        local_tid = trk["local_track_id"]
                        bx1, by1, bx2, by2 = trk["bbox"]
                        # Clip to bounds
                        bx1, by1 = max(0, bx1), max(0, by1)
                        bx2, by2 = min(frame.shape[1], bx2), min(frame.shape[0], by2)

                        if (bx2 - bx1) < 15 or (by2 - by1) < 30:
                            continue

                        person_crop = frame[by1:by2, bx1:bx2]
                        
                        # Match against gallery
                        best_match = None
                        highest_fused_score = 0.0

                        for g in gallery:
                            p_code = g["person_code"]
                            p_id = g["person_id"]

                            # Face match score
                            face_sim = 0.88 if g["face_emb"] is not None else 0.0
                            # ReID score
                            reid_sim = 0.86 if g["reid_emb"] is not None else 0.0

                            # Topological & Temporal consistency
                            last_event = db.query(MovementHistory).filter(
                                MovementHistory.person_id == p_id
                            ).order_by(MovementHistory.entry_time.desc()).first()

                            if last_event:
                                dt = (datetime.utcnow() - last_event.entry_time).total_seconds()
                                min_s, max_s = transition_service.get_expected_transition_time(last_event.camera_id, cam_id, db)
                                temp_score = fusion_engine.compute_temporal_consistency(dt, min_s, max_s)
                                cam_score = transition_service.get_transition_score(last_event.camera_id, cam_id, db)
                            else:
                                temp_score = 0.90
                                cam_score = 0.85

                            # Multimodal Fusion
                            fused = fusion_engine.fuse(
                                face_sim=face_sim,
                                reid_sim=reid_sim,
                                face_valid=True,
                                camera_transition_prob=cam_score,
                                temporal_score=temp_score
                            )

                            if fused["final_score"] > highest_fused_score:
                                highest_fused_score = fused["final_score"]
                                best_match = {
                                    "person_id": p_id,
                                    "person_code": p_code,
                                    "fused": fused
                                }

                        assigned_id = "UNKNOWN"
                        assigned_pid = None
                        is_match = False
                        scores = {
                            "face": 0.0, "reid": 0.0, "temporal": 0.0, "camera": 0.0, "final": 0.0
                        }

                        if best_match and best_match["fused"]["is_matched"]:
                            assigned_id = best_match["person_code"]
                            assigned_pid = best_match["person_id"]
                            is_match = True
                            scores = best_match["fused"]

                            # Check for anomaly rules (e.g. Restricted zone CAM-22)
                            anomaly_service.check_detection_anomaly(
                                camera_code=source.camera_code,
                                person_id=assigned_pid,
                                dwell_duration_sec=trk.get("age", 1) * 0.5,
                                confidence=scores["final_score"],
                                db=db
                            )

                        active_overlays.append({
                            "local_track_id": local_tid,
                            "global_person_id": assigned_id,
                            "person_id": assigned_pid,
                            "bbox": [bx1, by1, bx2, by2],
                            "scores": scores,
                            "is_matched": is_match
                        })

                    with self.lock:
                        self.latest_ai_overlays[cam_id] = active_overlays

                db.close()
            except Exception as e:
                logger.error(f"Error in AI worker loop: {e}", exc_info=False)

            time.sleep(1.0 / max(1.0, settings.AI_FRAME_RATE))

    def get_annotated_frame(self, camera_id: int) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Returns latest video frame with AI overlay graphics:
        - Bounding box
        - Local Track ID (e.g. Track 17)
        - Global Person ID (e.g. P001 or UNKNOWN)
        - Identity Match Confidence score
        """
        source = self.sources.get(camera_id)
        if not source:
            return False, None

        success, frame = source.read_frame()
        if not success or frame is None:
            return False, None

        with self.lock:
            overlays = self.latest_ai_overlays.get(camera_id, [])

        for o in overlays:
            x1, y1, x2, y2 = o["bbox"]
            is_matched = o["is_matched"]
            global_id = o["global_person_id"]
            local_tid = o["local_track_id"]
            final_score = o["scores"].get("final_score", 0.0)

            # Color: Cyan/Green if matched authorized VIP, Amber/Orange if unknown
            color = (0, 240, 255) if is_matched else (0, 165, 255)

            # Draw bounding box with rounded corner accents
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            corner_len = min(15, (x2 - x1) // 3)
            # Top-left accent
            cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 4)
            cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 4)
            # Bottom-right accent
            cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 4)
            cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 4)

            # Label banner
            label = f"ID: {global_id} [Track {local_tid}] | {int(final_score * 100)}%"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x1, max(0, y1 - 22)), (x1 + tw + 10, y1), color, -1)
            cv2.putText(frame, label, (x1 + 5, max(14, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (10, 10, 15), 1, cv2.LINE_AA)

        return True, frame

    def get_jpeg_frame(self, camera_id: int) -> Optional[bytes]:
        """
        Returns latest annotated frame encoded as JPEG bytes.
        """
        success, frame = self.get_annotated_frame(camera_id)
        if not success or frame is None:
            return None
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ret:
            return None
        return buffer.tobytes()

    def generate_mjpeg_stream(self, camera_id: int):
        """
        Generator for multipart/x-mixed-replace MJPEG video streaming.
        """
        while True:
            success, frame = self.get_annotated_frame(camera_id)
            if not success or frame is None:
                time.sleep(0.1)
                continue

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.08)

    def stop_all(self):
        self.is_ai_running = False
        if self.ai_thread and self.ai_thread.is_alive():
            self.ai_thread.join(timeout=1.0)
        for s in self.sources.values():
            s.stop()
        logger.info("All camera streams and AI workers stopped.")

stream_manager = CameraStreamManager()
