import cv2
import numpy as np
from typing import Optional

class FaceAligner:
    """
    Face aligner and canonical normalizer for ArcFace input (112x112).
    """
    def __init__(self, target_size: tuple = (112, 112)):
        self.target_size = target_size

    def align(self, face_img: np.ndarray, landmarks: Optional[np.ndarray] = None) -> np.ndarray:
        if face_img is None or face_img.size == 0:
            return np.zeros((self.target_size[1], self.target_size[0], 3), dtype=np.uint8)

        # If 5 facial landmarks are provided, apply similarity transformation
        if landmarks is not None and len(landmarks) == 5:
            # Reference landmarks for 112x112
            ref_pts = np.array([
                [38.2946, 51.6963],
                [73.5318, 51.5014],
                [56.0252, 71.7366],
                [41.5493, 92.3655],
                [70.7299, 92.2041]
            ], dtype=np.float32)
            M, _ = cv2.estimateAffinePartial2D(landmarks.astype(np.float32), ref_pts)
            if M is not None:
                aligned = cv2.warpAffine(face_img, M, self.target_size, borderValue=0.0)
                return aligned

        # Canonical resize fallback
        return cv2.resize(face_img, self.target_size, interpolation=cv2.INTER_LINEAR)
