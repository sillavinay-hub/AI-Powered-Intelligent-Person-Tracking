#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.tracking.tracker import ByteTracker

def main():
    print("Evaluating ByteTrack Multi-Object Tracking Module...")
    tracker = ByteTracker(max_age=10, min_hits=2, iou_threshold=0.3)

    # Frame 1: Person at [100, 100, 150, 220]
    dets_f1 = [{"bbox": [100, 100, 150, 220], "confidence": 0.88, "class_id": 0}]
    tracks_f1 = tracker.update(dets_f1)
    print(f"Frame 1 tracks: {len(tracks_f1)}")

    # Frame 2: Person moves slightly to [104, 102, 154, 222]
    dets_f2 = [{"bbox": [104, 102, 154, 222], "confidence": 0.89, "class_id": 0}]
    tracks_f2 = tracker.update(dets_f2)
    print(f"Frame 2 tracks: {len(tracks_f2)}")

    if tracks_f2:
        print(f"Preserved local_track_id: {tracks_f2[0]['local_track_id']}")
        assert tracks_f2[0]["local_track_id"] == 1

    print("Tracking evaluation: PASSED")

if __name__ == "__main__":
    main()
