import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from backend.config import settings
from backend.utils.logger import logger

class MultimodalIdentityFusionEngine:
    """
    Central Research Component: Multimodal Identity Association Engine.
    Fuses biometric face recognition, whole-body person ReID, temporal kinematics,
    and camera topological transition priors.

    Formula:
      identity_score = W_FACE * S_face + W_REID * S_reid + W_TEMP * S_temp + W_CAM * S_cam
    """
    def __init__(
        self,
        w_face: Optional[float] = None,
        w_reid: Optional[float] = None,
        w_temp: Optional[float] = None,
        w_cam: Optional[float] = None,
        identity_threshold: Optional[float] = None
    ):
        self.w_face = w_face if w_face is not None else settings.W_FACE
        self.w_reid = w_reid if w_reid is not None else settings.W_REID
        self.w_temp = w_temp if w_temp is not None else settings.W_TEMPORAL
        self.w_cam = w_cam if w_cam is not None else settings.W_CAMERA
        self.identity_threshold = identity_threshold if identity_threshold is not None else settings.IDENTITY_THRESHOLD

    def update_weights(self, w_face: float, w_reid: float, w_temp: float, w_cam: float):
        total = w_face + w_reid + w_temp + w_cam
        if total > 0:
            self.w_face = w_face / total
            self.w_reid = w_reid / total
            self.w_temp = w_temp / total
            self.w_cam = w_cam / total
        logger.info(f"Updated Fusion Weights: Face={self.w_face:.2f}, ReID={self.w_reid:.2f}, Temp={self.w_temp:.2f}, Cam={self.w_cam:.2f}")

    def compute_temporal_consistency(self, time_delta_sec: float, expected_min_sec: float, expected_max_sec: float) -> float:
        """
        Evaluates physical movement realism.
        If delta is within [expected_min, expected_max], high consistency score.
        If delta is near zero for distinct distant cameras, severe penalty (teleportation anomaly).
        """
        if time_delta_sec < 0:
            return 0.0

        # Same camera observation
        if expected_min_sec == 0 and expected_max_sec == 0:
            # Dwell time exponential decay
            return float(np.exp(-time_delta_sec / 600.0))

        # Too fast (impossible velocity)
        if time_delta_sec < (expected_min_sec * 0.5):
            ratio = max(0.0, time_delta_sec / max(1.0, expected_min_sec))
            return float(ratio ** 2 * 0.3)

        # In realistic walking window
        if expected_min_sec <= time_delta_sec <= expected_max_sec:
            return 0.95

        # Slower than max: gentle decay
        excess = time_delta_sec - expected_max_sec
        decay = float(np.exp(-excess / 300.0))
        return max(0.2, 0.95 * decay)

    def fuse(
        self,
        face_sim: float,
        reid_sim: float,
        face_valid: bool = True,
        camera_transition_prob: float = 0.5,
        temporal_score: float = 0.8,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Fuses modalities into unified explainable identity decision score.
        Dynamically adapts weights if face biometrics are occluded or unobserved.
        """
        wf = custom_weights.get("w_face", self.w_face) if custom_weights else self.w_face
        wr = custom_weights.get("w_reid", self.w_reid) if custom_weights else self.w_reid
        wt = custom_weights.get("w_temp", self.w_temp) if custom_weights else self.w_temp
        wc = custom_weights.get("w_cam", self.w_cam) if custom_weights else self.w_cam

        # Dynamic weight redistribution if face is occluded/invalid
        if not face_valid or face_sim <= 0.01:
            # Re-normalize across remaining modalities: ReID, Temporal, Camera
            non_face_sum = wr + wt + wc
            if non_face_sum > 0:
                eff_wf = 0.0
                eff_wr = wr / non_face_sum
                eff_wt = wt / non_face_sum
                eff_wc = wc / non_face_sum
            else:
                eff_wf, eff_wr, eff_wt, eff_wc = 0.0, 0.70, 0.15, 0.15
            effective_face_sim = 0.0
        else:
            total = wf + wr + wt + wc
            eff_wf = wf / total
            eff_wr = wr / total
            eff_wt = wt / total
            eff_wc = wc / total
            effective_face_sim = face_sim

        # Core fusion calculation
        final_score = (
            eff_wf * effective_face_sim +
            eff_wr * reid_sim +
            eff_wt * temporal_score +
            eff_wc * camera_transition_prob
        )
        final_score = float(np.clip(final_score, 0.0, 1.0))

        # Determine match status
        if final_score >= self.identity_threshold:
            status = "MATCH"
        elif final_score >= settings.UNKNOWN_THRESHOLD:
            status = "AMBIGUOUS"
        else:
            status = "UNKNOWN"

        return {
            "final_score": round(final_score, 3),
            "face_similarity": round(effective_face_sim, 3),
            "reid_similarity": round(reid_sim, 3),
            "temporal_score": round(temporal_score, 3),
            "camera_score": round(camera_transition_prob, 3),
            "effective_weights": {
                "w_face": round(eff_wf, 3),
                "w_reid": round(eff_wr, 3),
                "w_temporal": round(eff_wt, 3),
                "w_camera": round(eff_wc, 3)
            },
            "status": status,
            "is_matched": (status == "MATCH")
        }

fusion_engine = MultimodalIdentityFusionEngine()
