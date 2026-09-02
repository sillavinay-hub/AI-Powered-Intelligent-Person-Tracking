import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.ai.detection.config import DetectionConfig
from backend.ai.detection.postprocess import non_max_suppression
from backend.utils.logger import logger

class PersonDetector:
    """
    Person Detection Module using modern YOLO-compatible architecture with
    graceful CPU fallback (PyTorch / Color-Motion Saliency) for out-of-the-box local operation.
    """
    def __init__(self, config: Optional[DetectionConfig] = None):
        self.config = config or DetectionConfig()
        self.model = None
        self.is_yolo_loaded = False
        self.has_hog = hasattr(cv2, 'HOGDescriptor')
        self.hog = None
        self._init_detector()

    def _init_detector(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.is_yolo_loaded = True
            logger.info("Loaded YOLOv8n detector model successfully.")
        except Exception:
            if self.has_hog:
                try:
                    self.hog = cv2.HOGDescriptor()
                    self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                except Exception:
                    self.hog = None
            logger.info(f"Initialized PersonDetector fallback (YOLO: {self.is_yolo_loaded}, HOG: {self.hog is not None})")

    def detect(self, frame: np.ndarray, camera_id: int = 1) -> List[Dict[str, Any]]:
        """
        Runs person detection on input frame.
        Returns list of detections with format:
        {
            "bbox": [x1, y1, x2, y2],
            "confidence": float,
            "class_id": 0,
            "timestamp": datetime,
            "camera_id": camera_id
        }
        """
        if frame is None or frame.size == 0:
            return []

        now = datetime.utcnow()
        detections = []
        h, w = frame.shape[:2]

        if self.is_yolo_loaded and self.model is not None:
            try:
                results = self.model(frame, classes=[self.config.target_class_id], conf=self.config.confidence_threshold, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        b = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        if cls_id == self.config.target_class_id and conf >= self.config.confidence_threshold:
                            detections.append({
                                "bbox": [int(b[0]), int(b[1]), int(b[2]), int(b[3])],
                                "confidence": round(conf, 3),
                                "class_id": cls_id,
                                "timestamp": now,
                                "camera_id": camera_id
                            })
                return detections
            except Exception as e:
                logger.warning(f"YOLO inference error: {e}")

        # HOG fallback if available
        if self.hog is not None:
            try:
                scale = 1.0
                inf_frame = frame
                if w > 800:
                    scale = 640.0 / w
                    inf_frame = cv2.resize(frame, (640, int(h * scale)))

                rects, weights = self.hog.detectMultiScale(
                    inf_frame,
                    winStride=(8, 8),
                    padding=(8, 8),
                    scale=1.05
                )

                for (rx, ry, rw, rh), weight in zip(rects, weights):
                    conf = float(weight[0]) if hasattr(weight, '__iter__') else float(weight)
                    norm_conf = min(0.98, max(0.40, 0.5 + conf * 0.1))
                    if norm_conf >= self.config.confidence_threshold:
                        x1 = int(rx / scale)
                        y1 = int(ry / scale)
                        x2 = int((rx + rw) / scale)
                        y2 = int((ry + rh) / scale)
                        detections.append({
                            "bbox": [max(0, x1), max(0, y1), min(w, x2), min(h, y2)],
                            "confidence": round(norm_conf, 3),
                            "class_id": 0,
                            "timestamp": now,
                            "camera_id": camera_id
                        })
                return detections
            except Exception as e:
                logger.error(f"HOG detection error: {e}")

        return detections
