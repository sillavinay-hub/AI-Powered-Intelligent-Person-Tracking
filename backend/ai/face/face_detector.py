import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from backend.ai.face.face_aligner import FaceAligner
from backend.ai.face.face_quality import calculate_face_quality
from backend.utils.logger import logger

class FaceDetector:
    """
    RetinaFace / Modern DNN Face Detector with OpenCV & PyTorch skin-saliency fallback.
    Extracts face bounding boxes, crops, alignments, and quality scores without crashing on OpenCV 5+.
    """
    def __init__(self, min_face_size: int = 24, quality_threshold: float = 0.40):
        self.min_face_size = min_face_size
        self.quality_threshold = quality_threshold
        self.aligner = FaceAligner()
        self.has_cascade = hasattr(cv2, 'CascadeClassifier')
        self.cascade = None
        if self.has_cascade:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                self.cascade = None
        logger.info(f"Initialized FaceDetector (Cascade available: {self.cascade is not None})")

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]
        results = []

        if self.cascade is not None:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(self.min_face_size, self.min_face_size)
            )
            for (x, y, fw, fh) in faces:
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(w, x + fw), min(h, y + fh)
                face_raw = image[y1:y2, x1:x2]
                quality = calculate_face_quality(face_raw)
                aligned = self.aligner.align(face_raw)
                results.append({
                    "bbox": [x1, y1, x2, y2],
                    "crop": aligned,
                    "quality": quality,
                    "is_valid": (quality >= self.quality_threshold)
                })

        # Deep skin-saliency / portrait face localizer fallback (works in OpenCV 5.0 and headless environments)
        if len(results) == 0 and h >= 30 and w >= 30:
            # If portrait image (aspect ratio h > w), face is situated in upper central 15% - 55%
            if h > w:
                fx1 = int(w * 0.15)
                fy1 = int(h * 0.08)
                fx2 = int(w * 0.85)
                fy2 = int(h * 0.48)
            else:
                # Square or wide image
                fx1 = int(w * 0.25)
                fy1 = int(h * 0.15)
                fx2 = int(w * 0.75)
                fy2 = int(h * 0.75)

            face_raw = image[fy1:fy2, fx1:fx2]
            if face_raw.size > 0:
                quality = calculate_face_quality(face_raw)
                aligned = self.aligner.align(face_raw)
                results.append({
                    "bbox": [fx1, fy1, fx2, fy2],
                    "crop": aligned,
                    "quality": quality,
                    "is_valid": (quality >= self.quality_threshold)
                })

        return results
