import numpy as np
from typing import List, Dict, Any, Tuple
from backend.ai.tracking.kalman import KalmanBoxTracker

def calculate_iou(bb_test: list, bb_gt: list) -> float:
    # [x1, y1, x2, y2]
    xx1 = max(bb_test[0], bb_gt[0])
    yy1 = max(bb_test[1], bb_gt[1])
    xx2 = min(bb_test[2], bb_gt[2])
    yy2 = min(bb_test[3], bb_gt[3])
    w = max(0.0, xx2 - xx1)
    h = max(0.0, yy2 - yy1)
    intersection = w * h

    area1 = (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
    area2 = (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1])
    union = area1 + area2 - intersection
    if union <= 0:
        return 0.0
    return intersection / union

class ByteTracker:
    """
    ByteTrack-style Multi-Object Tracker for individual camera streams.
    Maintains local track identities (local_track_id).
    Local track IDs are independent across different cameras.
    """
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: List[KalmanBoxTracker] = []
        self.frame_count = 0

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.frame_count += 1
        
        # 1. Get predicted locations from existing trackers
        trks = np.zeros((len(self.trackers), 4))
        to_del = []
        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            trks[t, :] = [pos[0], pos[1], pos[2], pos[3]]
            if np.any(np.isnan(pos)):
                to_del.append(t)
        
        for t in reversed(to_del):
            self.trackers.pop(t)
            trks = np.delete(trks, t, axis=0)

        # 2. Separate detections into high-score and low-score (ByteTrack approach)
        high_dets = []
        low_dets = []
        for det in detections:
            if det.get("confidence", 0.0) >= 0.5:
                high_dets.append(det)
            else:
                low_dets.append(det)

        matched, unmatched_dets, unmatched_trks = self._associate(high_dets, trks, self.iou_threshold)

        # 3. Second association with remaining tracks and low-score detections
        if len(low_dets) > 0 and len(unmatched_trks) > 0:
            low_trks = trks[unmatched_trks]
            matched_low, _, remaining_unmatched_trks = self._associate(low_dets, low_trks, 0.2)
            # Map low-score matches back
            for d_idx, t_idx in matched_low:
                real_trk_idx = unmatched_trks[t_idx]
                matched.append((d_idx, real_trk_idx))
                # Update tracker with low-det
                self.trackers[real_trk_idx].update(low_dets[d_idx]["bbox"])
            unmatched_trks = [unmatched_trks[i] for i in remaining_unmatched_trks]

        # Update matched trackers
        for d_idx, t_idx in matched:
            if d_idx < len(high_dets):
                self.trackers[t_idx].update(high_dets[d_idx]["bbox"])

        # 4. Create new trackers for unmatched high-confidence detections
        for i in unmatched_dets:
            trk = KalmanBoxTracker(high_dets[i]["bbox"])
            self.trackers.append(trk)

        # 5. Formulate outputs and prune old tracks
        output_tracks = []
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = trk.get_state()
            if trk.time_since_update < 1 and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                output_tracks.append({
                    "local_track_id": trk.id,
                    "bbox": d,
                    "age": trk.age,
                    "hits": trk.hits
                })
            i -= 1
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)

        return output_tracks

    def _associate(self, detections: List[Dict[str, Any]], trackers: np.ndarray, threshold: float) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        if len(trackers) == 0:
            return [], list(range(len(detections))), []
        if len(detections) == 0:
            return [], [], list(range(len(trackers)))

        iou_matrix = np.zeros((len(detections), len(trackers)), dtype=float)
        for d, det in enumerate(detections):
            for t in range(len(trackers)):
                iou_matrix[d, t] = calculate_iou(det["bbox"], trackers[t])

        matched_indices = []
        unmatched_detections = []
        unmatched_trackers = list(range(len(trackers)))

        for d in range(len(detections)):
            best_t = -1
            best_iou = threshold
            for t in unmatched_trackers:
                if iou_matrix[d, t] > best_iou:
                    best_iou = iou_matrix[d, t]
                    best_t = t
            if best_t != -1:
                matched_indices.append((d, best_t))
                unmatched_trackers.remove(best_t)
            else:
                unmatched_detections.append(d)

        return matched_indices, unmatched_detections, unmatched_trackers
